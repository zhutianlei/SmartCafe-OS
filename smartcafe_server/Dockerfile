FROM node:18-alpine

LABEL \
  io.hass.version="1.0.0" \
  io.hass.type="app" \
  io.hass.arch="amd64"

WORKDIR /app
COPY server/ ./
RUN npm install --production

RUN mkdir -p /data/smartcafe-server

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
