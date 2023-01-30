FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./etl ${LAMBDA_TASK_ROOT}/etl
RUN ls -l ${LAMBDA_TASK_ROOT}

# https://docs.aws.amazon.com/lambda/latest/dg/runtimes-images.html#runtimes-api-client
# NOTE: To give controll back to "lambda interface client" in container just uncomment the CMD and comment out ENTRYPOINT

#CMD [ "etl.main.handler" ]
ENTRYPOINT []
