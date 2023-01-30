import json
import logging
import sys
from json import JSONDecodeError

from etl.core.event_handlers import NewPartnerHandler
from etl.exceptions import CoreException

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


def handler(event, context):
    # One option is to add another layer of abstraction to handle any kind of events:
    #   * s3_event
    #   * sqs_event
    #   * http_invoke_event
    #   * etc.
    # by defining a builtin Event() object and map `event` argument to builtin `Event` object.
    # Ofcourse it is not needed yet!

    logger.info("Received new event - type %s - %s", type(event), str(event))
    # In case the `event` is not converted to dict by lambda runtime
    if isinstance(event, str):
        try:
            event = json.loads(event)
        except JSONDecodeError as e:
            logger.error(e)
            return {
                "success": False,
                "msg": repr(e)
            }

    # Parse SQS and S3 events based on:
    #   https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
    #   https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-content-structure.html
    s3_events = []
    try:
        sqs_records = event["Records"]
        for record in sqs_records:
            body = record["body"]
            if not isinstance(body, dict):
                # In case body is not loaded by lambda runtime
                body = json.loads(body)
            s3_events.extend([record for record in body["Records"]])
    except (KeyError, JSONDecodeError) as e:
        logger.error(e)
        return {"success": False, "msg": repr(e)}

    for s3_event in s3_events:
        if s3_event.get("eventSource") != "aws:s3":
            logger.warning("Received a non-s3 event")
            continue
        # Dispatching ...
        # NOTE: Since we only have one handler, there is no need to dispatch any handlers here.
        h = NewPartnerHandler(s3_event)
        try:
            h.run()
        except CoreException as e:
            logger.error(e)
            # Handle retry mechanism by propagating the exception to lambda runtime.
            # In this way, s3 notification will not automatically be deleted from sqs.
            if e.propagate:
                raise

    return {"success": True}
