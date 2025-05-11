from totp_sync import get_secret_key
from tor_manager import start_hidden_service, connect_to_peer


def main():
    token = get_secret_key()
    onion_prefix = token.lower()  # e.g., 'abc123'

    print(f"[INFO] TOTP handshake token: {token}")

    # Start Tor with onion address matching token
    onion_address = start_hidden_service(prefix=onion_prefix)
    print(f"[INFO] Hidden Service started: {onion_address}")

    # Try to connect to the other peer with same token
    connect_to_peer(onion_prefix)


if __name__ == "__main__":
    main()
