FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --upgrade google-cloud-storage
RUN pip install --upgrade google-api-python-client
ADD . /code/
