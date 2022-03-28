ARG PYTHON_VER=3.8

FROM python:${PYTHON_VER}-slim

RUN pip install --upgrade pip

WORKDIR /local
COPY . /local

RUN pip install .