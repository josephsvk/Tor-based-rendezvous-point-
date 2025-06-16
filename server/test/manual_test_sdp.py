#!/usr/bin/env python3
"""
manual_test_sdp.py

Manual WebSocket SDP tester over Tor using aiohttp-socks.

Usage:
  1. Ensure FastAPI server is running (e.g., `uvicorn fastapi_app:app --host 0.0.0.0 --port 8000`).
  2. Run this script: `./manual_test_sdp.py`.
  3. Or use `websocat`:
     `websocat -s 127.0.0.1:9050 ws://<ONION>/webrtc/sdp/manual_client`
"""
import asyncio
import json
import sys
from pathlib import Path

import aiohttp
from aiohttp_socks import ProxyConnector

# Load onion hostname
onion_file = Path('.tor_service/hostname.txt')
if not onion_file.exists():
    print(f"Error: {onion_file} not found.")
    sys.exit(1)
ONION = onion_file.read_text().strip()

# WebSocket URI
client_id = 'manual_client'
# Include port 80 for Onion service
uri = f"ws://{ONION}:80/webrtc/sdp/{client_id}"

async def main():
    connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
    timeout = aiohttp.ClientTimeout(total=15)
    print(f"Connecting to {uri} via Tor...")
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        try:
            async with session.ws_connect(uri) as ws:
                msg = await ws.receive_json()
                print('Received offer:', msg)
                answer = {'type': 'answer', 'sdp': 'manual_answer_sdp'}
                print('Sending answer:', answer)
                await ws.send_json(answer)
                await ws.close()
                print('WebSocket closed.')
        except Exception as e:
            print('Error:', e)

if __name__ == '__main__':
    asyncio.run(main())
