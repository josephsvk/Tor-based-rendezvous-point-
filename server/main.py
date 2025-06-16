# -*- coding: utf-8 -*-
"""
Hlavný modul na spustenie Tor V3 hidden service a FastAPI servera.
"""
from datetime import datetime, timezone
from pathlib import Path
from stem.control import Controller
from tor_service import main as preparate_tor_service
from fastapi_app import app
import uvicorn


def get_current_time_window() -> str:
    """
    Vráti aktuálne časové okno vo formáte RRRR-MM.

    Returns:
        str: Časové okno, napr. "2025-05".
    """
    return datetime.now(timezone.utc).strftime("%Y-%m")


def read_file(path: Path) -> str:
    """
    Načíta obsah súboru ako reťazec.

    Args:
        path (Path): Cesta k súboru.

    Returns:
        str: Obsah súboru.
    """
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    """
    Spustí generovanie Tor kľúčov, vytvorí ephemeral hidden service
    a spustí FastAPI server v rámci samej Tor kontrolnej relácie.
    """
    print("[INFO] Spúšťam generovanie Tor kľúčov a onion adresy...")
    preparate_tor_service()

    service_dir = Path(".tor_service")
    private_key_path = service_dir / "private_key.txt"
    hostname_path = service_dir / "hostname.txt"

    if not private_key_path.exists() or not hostname_path.exists():
        raise FileNotFoundError(
            f"Chýbajúce súbory: {private_key_path} alebo {hostname_path}"
        )

    private_key = read_file(private_key_path)
    print(f"[INFO] Načítaný Tor kľúč: {private_key}")

    expected_hostname = read_file(hostname_path)
    print(f"[INFO] Očakávaná adresa: {expected_hostname}")

    # Pripojenie k Tor kontrolnému portu a beh služby
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        print("[INFO] Pripojenie k Tor kontrolnému portu úspešné.")

        hidden_service = controller.create_ephemeral_hidden_service(
            ports={80: 5000},
            key_type='ED25519-V3',
            key_content=private_key,
            await_publication=True,
        )

        onion_address = f"{hidden_service.service_id}.onion"
        print(f"[INFO] Hidden service spustený na: {onion_address}")

        if onion_address != expected_hostname:
            print(
                f"[WARNING] Adresa sa nezhoduje s očakávanou: {expected_hostname}"
            )

        # Spustenie FastAPI servera v rámci otvorenej relácie Tor kontroly
        print("[INFO] Spúšťam FastAPI server na porte 5000... Ctrl+C pre ukončenie.")
        try:
            uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
        except KeyboardInterrupt:
            print("\n[INFO] Vypínam FastAPI server a hidden service…")
            # Controller context ukončí službu pri zatvorení


if __name__ == "__main__":
    main()