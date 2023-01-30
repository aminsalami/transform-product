import json
import logging

import boto3
from botocore.exceptions import ClientError

from etl.config import config
from etl.core.dto import ProductData
from etl.exceptions import RepoException
from etl.ports import ReadOnlyRepo, WriteOnlyRepo

logger = logging.getLogger(__name__)


class S3ReadFileRepo(ReadOnlyRepo):
    """
    Downloads a file from s3 by implementing the ReadOnly interface.
    """

    def __init__(self, bucket_name: str, s3_client=None):
        self.bucket_name = bucket_name
        if s3_client:
            self.s3 = s3_client
        else:
            self.s3 = boto3.client("s3", endpoint_url=config["AWS_ENDPOINT_URL"])

    def get(self, key, **kwargs):
        # Retrieve file content without downloading it to /tmp
        logger.info("Trying to retrieve `%s` from s3", key)
        try:
            obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            data = obj['Body'].read().decode('utf-8')
        except ClientError as e:
            raise RepoException(e)
        return data


class S3ProductRepo(WriteOnlyRepo):
    def __init__(self, bucket_name: str, s3_client=None):
        self.bucket_name = bucket_name
        if not s3_client:
            self.s3 = boto3.client("s3", endpoint_url=config["AWS_ENDPOINT_URL"])
        else:
            self.s3 = s3_client

    def save(self, data: [ProductData], name, **kwargs):
        logger.info("Saving `%s` products as json to bucket:`%s`", len(data), self.bucket_name)
        json_data = json.dumps([p.to_dict() for p in data])
        if not json_data:
            return
        try:
            self.s3.put_object(Body=json_data, Bucket=self.bucket_name, Key=name)
        except Exception as e:
            logger.error("cannot put object into `%s` bucket - %s", self.bucket_name, e)
