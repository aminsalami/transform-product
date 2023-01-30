import os

# A simple dict to load configs
config = {
    "AWS_ENDPOINT_URL": os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),

    "SOURCE_BUCKET": os.environ.get("SOURCE_BUCKET", "sourcebucket"),
    "DEST_BUCKET": os.environ.get("DESTINATION_BUCKET", "destinationbucket"),
}
