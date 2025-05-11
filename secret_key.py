import os

# Získanie tajného kľúča z environmentálnej premennej
secret_key = os.getenv("SECRET_KEY")

if secret_key:
    print(f"Tajný kľúč je: {secret_key}")
else:
    print("Tajný kľúč nebol nastavený! Skontrolujte konfiguráciu.")