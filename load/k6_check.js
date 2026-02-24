import http from "k6/http";
import { check, sleep } from "k6";

const VUS = Number(__ENV.VUS || 20);
const DURATION = __ENV.DURATION || "20s";

export const options = {
  vus: VUS,
  duration: DURATION,
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<50"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost:8000";
const URL = `${BASE}/api/check`;

export default function () {
  const key = `user-${toggle()}`; // reduce hot-key contention
  const payload = JSON.stringify({ key, cost: 1 });

  const res = http.post(URL, payload, {
    headers: { "Content-Type": "application/json" },
  });

  check(res, {
    "status is 200": (r) => r.status === 200,
  });

  sleep(0.01);
}

let i = 0;
function toggle() {
  i = (i + 1) % 50;
  return i;
}
