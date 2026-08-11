FROM debian/eol:etch

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libssl-dev \
    zlib1g-dev

ARG PYVER

COPY Python-${PYVER}.tgz .

RUN tar xzf Python-${PYVER}.tgz && \
    cd Python-${PYVER} && \
    ./configure --prefix=/usr/local/python-${PYVER} && \
    make && \
    make install

# Python in PATH setzen
ENV PATH="/usr/local/python-${PYVER}/bin:${PATH}"

WORKDIR /app
