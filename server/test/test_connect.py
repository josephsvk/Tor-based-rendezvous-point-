"""Skúška HTTP GET požiadavky cez Tor SOCKS5 proxy s retry."""
import time
import requests
from pathlib import Path

base_dir = Path(".tor_service")
private_key_path = base_dir / "private_key.txt"
hostname_path = base_dir / "hostname.txt"
print(private_key_path, hostname_path)

ONION = hostname_path.read_text().strip()

PROXIES = {
    "http":  "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

print("Testujem onion:", ONION)
MAX_RETRIES = 12
for attempt in range(1, MAX_RETRIES + 1):
    try:
        resp = requests.get(f"http://{ONION}/", proxies=PROXIES, timeout=10)
        print(f"[SUCCESS] Status code: {resp.status_code}")
        print(resp.text[:200], "…")
        break
    except Exception as e:
        print(f"[{attempt}/{MAX_RETRIES}] Chyba: {e}")
        time.sleep(5)
else:
    print(f"[FAIL] Nedarí sa pripojiť po {MAX_RETRIES*5}s. Skontroluj Tor logy a stav HSDir publikácie.")
