FROM ubuntu:latest

ARG AUTOMEDIA_VERSION
ADD dist/automedia-${AUTOMEDIA_VERSION}-py3-none-any.whl /tmp/

RUN apt-get update \
    && apt-get install --no-install-recommends --yes python3 pip par2 \
    && apt-get install --yes ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install /tmp/automedia-${AUTOMEDIA_VERSION}-py3-none-any.whl \
    && rm /tmp/*.whl

ENTRYPOINT [ "automedia" ]
