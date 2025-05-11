import os

# Získanie tajného kľúča z environmentálnej premennej
secret_key = os.getenv("MY_SECRET_KEY")

if secret_key:
    print(f"Tajný kľúč je nastavený")
else:
    print("Tajný kľúč nebol nastavený! Skontrolujte konfiguráciu.")
