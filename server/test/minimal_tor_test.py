from stem.control import Controller
import traceback

# Použijeme kľúč z vášho logu
TEST_KEY_B64 = "MiB9dOf0fiCDI5HhkGZ9zKihH6x8+F3cKevSyTaNlWI="
# Alternatívne môžete vygenerovať úplne nový náhodný 32-bajtový kľúč a base64 ho zakódovať.

print(f"Tor Kľúč pre test: {TEST_KEY_B64}")

try:
    with Controller.from_port(port=9051) as controller:
        controller.authenticate() # Uistite sa, že autentifikácia je správne nastavená pre váš Tor control port
        print("Úspešne pripojený a autentifikovaný k Tor control portu.")

        print(f"Pokus o pridanie onion služby s kľúčom: {TEST_KEY_B64}")
        hidden_service = controller.create_ephemeral_hidden_service(
            ports={80: 1234},  # Mapovanie portov je len pre test
            key_type='ED25519-V3',
            key_content=TEST_KEY_B64,
            await_publication=True # Počká na publikovanie (môže chvíľu trvať)
        )
        print(f"Úspešne vytvorená skrytá služba: {hidden_service.service_id}.onion")

        # Upratanie
        controller.remove_ephemeral_hidden_service(hidden_service.service_id)
        print(f"Skrytá služba {hidden_service.service_id}.onion bola odstránená.")

except Exception as e:
    print(f"Nastala chyba: {e}")
    traceback.print_exc()