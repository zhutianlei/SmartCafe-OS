const http = require('http');
const { getConfig, getWhitelist } = require('./storage');
const { getHaTokens } = require('./ha_auth');

const ENTITY_ID = 'sensor.smartcafe_devices';
let heartbeatTimer = null;

function httpRequest(urlStr, data, method = 'POST', token = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const postData = data ? JSON.stringify(data) : null;
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: url.pathname + (url.search || ''),
      method,
      headers
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(body) }); }
        catch { resolve({ status: res.statusCode, data: body }); }
      });
    });
    req.on('error', reject);
    if (postData) req.write(postData);
    req.end();
  });
}

async function pushDeviceList() {
  const config = getConfig();
  if (!config.ha_username || !config.ha_password) return;

  const haBase = config.ha_base_url.replace(/\/$/, '');
  let token;
  try {
    const tokens = await getHaTokens(config.ha_username, config.ha_password);
    token = tokens.access_token;
  } catch (e) {
    console.error('[Heartbeat] 获取Token失败:', e.message);
    return;
  }

  const whitelist = getWhitelist();
  const devices = whitelist
    .filter(item => item.ip)
    .map(item => ({
      ip: item.ip,
      mac: item.mac || '',
      name: item.name || item.ip,
      category: item.category || '',
      client_enabled: item.client_enabled !== false
    }));

  const state = devices.length > 0 ? 'online' : 'offline';
  const attributes = {
    devices,
    device_count: devices.length,
    friendly_name: '智咖系统设备列表'
  };

  try {
    const res = await httpRequest(
      `${haBase}/api/states/${ENTITY_ID}`,
      { state, attributes, icon: 'mdi:monitor-dashboard' },
      'POST',
      token
    );
    if (res.status === 200 || res.status === 201) {
      console.log(`[Heartbeat] 设备列表已同步: ${devices.length} 台设备`);
    } else {
      console.error(`[Heartbeat] 同步失败: HTTP ${res.status}`);
    }
  } catch (e) {
    console.error('[Heartbeat] 同步异常:', e.message);
  }
}

function startHeartbeat(intervalMs = 30000) {
  if (heartbeatTimer) clearInterval(heartbeatTimer);
  console.log(`[Heartbeat] 启动心跳，间隔 ${intervalMs / 1000}s`);

  pushDeviceList();
  heartbeatTimer = setInterval(pushDeviceList, intervalMs);
}

function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }
}

module.exports = { startHeartbeat, stopHeartbeat, pushDeviceList };
