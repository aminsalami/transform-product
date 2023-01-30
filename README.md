### How to run?

Start the localstack using compose:

`[sudo] docker compose up --build`

then setup the services by running "init.bash" file in the current directory:

`bash init.bash`

* It will create 2 buckets, source and destination
* A SQS queue with fixed arn: "ARN:arn:aws:sqs:eu-west-1:000000000000:convert2json_queue"
* and a lambda function named `convert2json` which will be invoked by SQS

Since it is not possible to deploy a lambda function on localstack (free-tier) using Docker images, the script generates a "deployment-package.zip" before creating the lambda function.

Note that, env variables are defined in this file. Default variables:

```
AWS_ENDPOINT_URL=http://localhost:4566
SOURCE_BUCKET=sourcebucket
DESTINATION_BUCKET=destinationbucket
SQS_QUEUE_NAME=convert2json_queue
```

I executed this command to follow the lambda logs (after the first lambda run):
`aws --endpoint-url=http://localhost:4566 logs tail '/aws/lambda/convert2json' --follow`


### Run tests

`docker run -it $(docker build -q .) python3 -m unittest discover .`

### Notes
The project utilizes AWS Lambda, SQS, and S3 to convert xml files. Instead of long-polling the new events happening on s3, its been configured to send notifications.
Here is my reasons for choosing these tools:
* Events coming from S3 should be persistent somehow. We don't want to miss any uploaded file in case the worker is down. A high-available queue is the best option here.
* With SQS we can send files that can't be processed to a DeadLetterQueue for further debugging. Although this project didn't utilize a DLQ, I learned about this option and I think it's a good fit here.
* Based on the frequently of *.XML files uploaded to S3, Lambda is the cheapest/scalable option. We dont want to run a worker for 24/7 on a server to handle 8 files per day.
* Another solution that came to my mind at first, was to implement a long-polling process to receive events from queue, and then notify celery workers (through a message broker).
I think this solution is more suitable for long-running tasks or when we really need a high throughput scenario. I didn't choose this option since workers and dispatchers need to be alive all the time, therefore, the cost would be high.

Around code & architecture:
* Extendability and being Maintainable was my mindset during the development. Any third-party tools (such as databases, APIs, etc) should be dependent to interfaces/ports defined by the core, not the other way around.
Moreover, I think having immutable data-objects for every stage (load, transform) will be more clean.
I assumed some fields in raw xml are required. A "invalid XML exception" will be thrown if they are not present.
* Some exceptions are not handled intentionally so that the lambda runtime does not delete the SQS message. We handle retry mechanism in this way.
