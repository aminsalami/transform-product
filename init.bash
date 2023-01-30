REGION=eu-west-1

echo "-> loading env variables"
#source env.env
AWS_ENDPOINT_URL=http://localhost:4566
REGION=eu-west-1
SOURCE_BUCKET=sourcebucket
DESTINATION_BUCKET=destinationbucket
SQS_QUEUE_NAME=convert2json_queue


echo "------------------------"
echo "-> Create a source bucket"
aws --endpoint-url=$AWS_ENDPOINT_URL s3api create-bucket --bucket $SOURCE_BUCKET --region $REGION --create-bucket-configuration LocationConstraint=$REGION

echo "------------------------"
echo "-> Create a destination bucket"
aws --endpoint-url=$AWS_ENDPOINT_URL s3api create-bucket --bucket $DESTINATION_BUCKET --region $REGION --create-bucket-configuration LocationConstraint=$REGION

#echo "------------------------"
#echo "-> list buckets"
#aws --endpoint-url=$AWS_ENDPOINT_URL s3api list-buckets

echo "------------------------"
echo "-> create a queue"
aws --endpoint-url=$AWS_ENDPOINT_URL sqs create-queue --queue-name $SQS_QUEUE_NAME

echo "------------------------"
echo "-> Configure s3 to send notifications to SQS"
TMP='{"QueueConfigurations": [{"QueueArn": "arn:aws:sqs:eu-west-1:000000000000:'"${SQS_QUEUE_NAME}"'", "Events": ["s3:ObjectCreated:*"]}]}'
aws --endpoint-url=$AWS_ENDPOINT_URL s3api put-bucket-notification-configuration --bucket $SOURCE_BUCKET --notification-configuration "$TMP"

echo "------------------------"
echo "-> Creating a python zip package"
bash create_zip_package.bash

echo "------------------------"
echo "-> Create a new lambda"
aws --endpoint-url=$AWS_ENDPOINT_URL lambda create-function --function-name convert2json --runtime python3.9 --zip-file fileb://deployment-package.zip --handler etl.main.handler --timeout 7 --role x1 \
  --environment "Variables={AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL},SOURCE_BUCKET=${SOURCE_BUCKET},DESTINATION_BUCKET=${DESTINATION_BUCKET}}"

echo "------------------------"
echo "-> Configure SQS to send notifications to the lambda function"
aws --endpoint-url=$AWS_ENDPOINT_URL lambda create-event-source-mapping --function-name convert2json --event-source-arn arn:aws:sqs:eu-west-1:000000000000:"${SQS_QUEUE_NAME}"

echo "------------------------"
echo "-> DONE :)"
