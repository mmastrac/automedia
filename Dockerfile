FROM ubuntu:latest

RUN apt-get update \
    && apt-get install --no-install-recommends --yes python3 par2 \
    && apt-get install --yes ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ADD automedia /__application__/
ADD src/*.py /__application__/src/

ENTRYPOINT [ "/__application__/automedia" ]
