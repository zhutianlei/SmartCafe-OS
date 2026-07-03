FROM ghcr.io/home-assistant/amd64-base:latest

RUN apk add --no-cache nodejs npm

WORKDIR /app
COPY server/ ./
RUN npm ci --omit=dev || npm install

RUN mkdir -p /data/smartcafe-server

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
