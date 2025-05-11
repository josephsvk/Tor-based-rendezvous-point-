import os
import subprocess
from pathlib import Path

def start_hidden_service(prefix):
    """
    Pokús sa najsť či existuje onion adresa s prefixom TOTP.
    Ak nie, vygeneruj pomocou mkp224o a naštartuj hidden service.
    """
    hs_dir = Path("hidden_service") / prefix
    hs_dir.mkdir(parents=True, exist_ok=True)

    private_key = hs_dir / "hs_ed25519_secret_key"
    hostname = hs_dir / "hostname"

    if not hostname.exists():
        print(f"[INFO] Generating new .onion address with prefix '{prefix}'")
        subprocess.run([
            "mkp224o", prefix,
            "--output", str(hs_dir),
            "--threads", "2"
        ], check=True)

    torrc_path = Path("torrc")
    with torrc_path.open("w") as f:
        f.write(f"HiddenServiceDir {hs_dir.resolve()}\n")
        f.write("HiddenServicePort 2222 127.0.0.1:2222\n")

    subprocess.Popen(["tor", "-f", str(torrc_path)])

    return hostname.read_text().strip()

def connect_to_peer(token_prefix):
    """
    Pokus o pripojenie na peer .onion adresu vytvorenú z TOTP tokenu
    """
    print(f"[INFO] Attempting to connect to peer {token_prefix}*.onion")
    # Tu bude čakanie na spojenie alebo outbound pripojenie - neskôr implementácia
    pass