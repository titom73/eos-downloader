ARG PYTHON_VER=3.8

FROM python:${PYTHON_VER}-slim

RUN pip install --upgrade pip \
  && pip install poetry

WORKDIR /local
COPY . /local

RUN pip install .