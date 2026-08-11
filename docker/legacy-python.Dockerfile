FROM debian/eol:etch

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libssl-dev \
    zlib1g-dev

ARG PYVER

# Alte Python-Version herunterladen und bauen
RUN wget http://github.com/kindermaenner/rorpy/releases/download/legacy-python-src/python-${PYVER}.tgz && \
    tar xzf python-${PYVER}.tgz && \
    cd python-${PYVER} && \
    ./configure --prefix=/usr/local/python-${PYVER} && \
    make && \
    make install

# Python in PATH setzen
ENV PATH="/usr/local/python-${PYVER}/bin:${PATH}"

WORKDIR /app
