import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '20s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<50'], // adjust target after you measure baseline
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const URL = `${BASE}/api/check`;

export default function () {
  const key = `user-${_toggle()}`; // reduce hot-key contention a bit
  const payload = JSON.stringify({ key: key, cost: 1 });

  const res = http.post(URL, payload, { headers: { 'Content-Type': 'application/json' } });

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(0.01);
}

let i = 0;
function _toggle() {
  i = (i + 1) % 50;
  return i;
}
