FROM ubuntu:20.04

ARG PYVER

RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev

# Alte Python-Version herunterladen und bauen
RUN wget https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tgz && \
    tar xzf Python-${PYVER}.tgz && \
    cd Python-${PYVER} && \
    ./configure --prefix=/usr/local/python-${PYVER} && \
    make && \
    make install

# Python in PATH setzen
ENV PATH="/usr/local/python-${PYVER}/bin:${PATH}"

WORKDIR /app
