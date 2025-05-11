import pyotp
import os
import subprocess


def get_secret_key():
    """Načíta TOTP tajný kľúč z premennej prostredia 'TOTP'."""
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise EnvironmentError("[ERROR] Env variable TOTP not found. Did you set the GitHub secret?")
    return secret

