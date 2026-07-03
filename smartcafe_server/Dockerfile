ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

LABEL \
  io.hass.version="1.0.0" \
  io.hass.type="app" \
  io.hass.arch="amd64"

RUN apk add --no-cache nodejs npm

WORKDIR /opt/server
COPY ./server/package.json ./
RUN npm install

COPY ./server/ ./
RUN mkdir -p /data/smartcafe-server

COPY ./run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
