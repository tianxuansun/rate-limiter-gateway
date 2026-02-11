import time

import requests

BASE = "http://localhost:8000"


def call_enforce(key: str, cost: float = 1.0):
    r = requests.post(f"{BASE}/api/enforce", json={"key": key, "cost": cost})
    return r


def main():
    key = "demo-user"
    for i in range(10):
        r = call_enforce(key, 1)
        print(i, r.status_code, r.json(), "Retry-After:", r.headers.get("Retry-After"))
        if r.status_code == 429:
            sleep_s = int(r.headers.get("Retry-After", "1"))
            time.sleep(sleep_s)


if __name__ == "__main__":
    main()
