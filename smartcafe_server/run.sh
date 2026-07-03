#!/command/with-contenv bashio
# shellcheck shell=bash

# Read options from Supervisor
CONFIG_PATH=/data/options.json

# Get HA configuration
HA_BASE_URL=$(bashio::config 'ha_base_url')
HA_USERNAME=$(bashio::config 'ha_username')
HA_PASSWORD=$(bashio::config 'ha_password')
TOKEN_REFRESH_TIME=$(bashio::config 'token_refresh_time')

mkdir -p /data/smartcafe-server
cat > /data/smartcafe-server/config.json << EOF
{
  "ha_base_url": "${HA_BASE_URL}",
  "ha_username": "${HA_USERNAME}",
  "ha_password": "${HA_PASSWORD}",
  "token_refresh_time": "${TOKEN_REFRESH_TIME}",
  "port": 8765,
  "password_hash": "",
  "password_salt": ""
}
EOF

# Create empty data files if they don't exist
if [ ! -f /data/smartcafe-server/whitelist.json ]; then
  echo "[]" > /data/smartcafe-server/whitelist.json
fi

if [ ! -f /data/smartcafe-server/audit.json ]; then
  echo "[]" > /data/smartcafe-server/audit.json
fi

# Start the server
cd /opt/server
exec node server.js
