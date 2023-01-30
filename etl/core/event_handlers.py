import logging

from etl.config import config
from etl.core.dto import RawProduct
from etl.core.loaders import ProductXmlLoader
from etl.core.transformation import ProductTransformer
from etl.repositories.s3 import S3ReadFileRepo, S3ProductRepo

logger = logging.getLogger(__name__)


class NewPartnerHandler:
    """
    Coordinates "new partner company" events.

    This class specifically responsible for receiving s3 event from higher layer, fetching the *.XML file,
    converting to object, and finally storing it into another s3 location.
    """

    def __init__(self, e):
        self.e = e

    def run(self):
        """
        Coordinates the etl process.
        :return: None
        """
        key = self.e["s3"]["object"]["key"]
        logger.info("Received a new S3 event - %s - %s - %s", self.e["eventTime"], self.e["eventName"], key)

        # Create a new repository to work with the source bucket
        # source_repo = S3ReadRepo(bucket_name=config["SOURCE_BUCKET"])
        source_repo = S3ReadFileRepo(bucket_name=self.e["s3"]["bucket"]["name"])
        raw_xml = source_repo.get(self.e["s3"]["object"]["key"])

        # Load raw data received from repo to data-objects
        c = ProductXmlLoader(data_cls=RawProduct)
        products = c.load(raw_xml)

        # Convert to target product item, based on the rules
        dto = ProductTransformer().transform(products)

        # Save the data to another storage
        dest_repo = S3ProductRepo(bucket_name=config["DEST_BUCKET"])
        new_name = key.replace(".xml", ".json")
        dest_repo.save(dto, name=new_name)
        logger.info("Done.")
