ARG BASE_IMAGE_TAG=1.15.0-py3
FROM tensorflow/tensorflow:$BASE_IMAGE_TAG
RUN pip install --upgrade pip
RUN python3 -m pip install tensorflow==1.15.0
RUN python3 -m pip install tensorflow_transform==0.15.0
RUN python3 -m pip install apache_beam==2.16.0
COPY ./src /pipelines/component/src
