import subprocess

def block_emailf(email):
    try:
        # Agregamos el email a la lista negra
        with open("/etc/postfix/sender_access", "a") as blacklist_file:
            blacklist_file.write(f"{email} REJECT\n")

        # Creamos la base de datos con el comando postmap
        subprocess.run(["sudo", "postmap", "hash:/etc/postfix/sender_access"])
        
        print(f"El correo {email} ha sido bloqueado.")
    except Exception as e:
        print(f"Hubo un problema al cargar el email en la lista negra: {e}")