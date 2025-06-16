# -*- coding: utf-8 -*-
"""
Skript na generovanie deterministických Tor V3 hidden service kľúčov a onion adresy.
Kľúče a hostname sa ukladajú priamo do adresára `.tor_service`.
"""
import os
import hashlib
import base64
import datetime
from pathlib import Path
from nacl.signing import SigningKey
from dotenv import load_dotenv

# Načítame tajný kľúč z prostredia
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY env var not set.")


def get_seed(secret_key: str, time_window: str) -> bytes:
    """
    Generuje deterministický seed z tajného kľúča a časového okna.

    Args:
        secret_key: Tajné heslo alebo token.
        time_window: Reťazec vo formáte RRRR-MM.

    Returns:
        Binárny seed (32 bajtov) z SHA256(secret_key + time_window).
    """
    return hashlib.sha256(f"{secret_key}{time_window}".encode()).digest()


def clamp_scalar(h_bytes: bytes) -> bytes:
    """
    Aplikuje Ed25519 clamp na prvých 32 bajtov SHA512 digestu.
    """
    scalar = bytearray(h_bytes[:32])
    scalar[0] &= 248
    scalar[31] &= 127
    scalar[31] |= 64
    return bytes(scalar)


def export_tor_private_key(seed: bytes) -> str:
    """
    Vytvorí Tor-kompatibilný key_blob pre ED25519-V3 bez použitia subadresára.

    Args:
        seed: Binárny seed (32 bajtov).

    Returns:
        Base64 reťazec (88 znakov) pre ControlPort ADD_ONION.
    """
    # Z seed vypočítame scalar a prf_secret
    digest = hashlib.sha512(seed).digest()
    scalar = clamp_scalar(digest)
    prf_secret = digest[32:]
    blob = scalar + prf_secret  # 64 bajtov raw
    return base64.b64encode(blob).decode("ascii")


def generate_onion_address(seed: bytes) -> str:
    """
    Generuje V3 onion adresu z daného seedu.
    """
    signing_key = SigningKey(seed)
    pubkey = signing_key.verify_key.encode()
    checksum = hashlib.sha3_256(b".onion checksum" + pubkey + b"\x03").digest()[:2]
    addr_bytes = pubkey + checksum + b"\x03"
    addr_b32 = base64.b32encode(addr_bytes).decode("ascii").lower().rstrip("=")
    return f"{addr_b32}.onion"


def main() -> None:
    """
    Generuje a uloží hidden service kľúč a onion adresu do `.tor_service`.
    """
    now = datetime.datetime.utcnow()
    window = now.strftime("%Y-%m")

    # Adresár pre kľúče
    service_dir = Path(".tor_service")
    service_dir.mkdir(exist_ok=True)

    # Generovanie
    seed = get_seed(SECRET_KEY, window)
    tor_key = export_tor_private_key(seed)
    onion = generate_onion_address(seed)

    # Uloženie výsledkov
    (service_dir / "private_key.txt").write_text(tor_key)
    print(f"[DONE] Kľúč uložený v: {service_dir/'private_key.txt'}")

    (service_dir / "hostname.txt").write_text(onion)
    print(f"[DONE] Adresa uložená v: {service_dir/'hostname.txt'}")


if __name__ == "__main__":
    main()
