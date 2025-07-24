import subprocess
import os
import sys
# directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# directorio hips
parent_dir = os.path.dirname(current_dir)

# directorio controlar_logs
tools_dir = os.path.join(parent_dir, 'tools')
sys.path.append(tools_dir)
import send_csv_logs
import block_email
def block_email(email):
    try:
        # Agregamos el email a la lista negra
        with open("/etc/postfix/sender_access", "a") as blacklist_file:
            blacklist_file.write(f"{email} REJECT\n")

        # Creamos la base de datos con el comando postmap
        subprocess.run(["sudo", "postmap", blacklist_file])
        
        print(f"El correo {email} ha sido bloqueado.")
    except Exception as e:
        print(f"Hubo un problema al cargar el email en la lista negra: {e}")





def check_maillogg():
   
    command = "sudo cat /var/log/maillog.log | grep -i 'authid' " #filtro por authid
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Verificar si hubo errores en la ejecución del comando
    if process.returncode == 0:
    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
        file = process.stdout.split("\n")[:-1]
        print(file)
    else:
    # Si hubo un error, imprimir el mensaje de error
        print("Error al ejecutar el comando:")
        print(process.stderr)
    
    contador_email ={}

    #analizar linea por linea del contenido obtenido en file
    for email in file:
        email = [word for word in email.split() if 'authid=' in word][0]
        email = email.split("=")[-1][:-1] # Sacamos el 'authid=' y la ',' al final. Finalmente obtenemos el email.
        if email in contador_email:
            contador_email[email] = contador_email[email] + 1
            if contador_email[email] == 30:
                #block_email.block_emailf(email)
                send_csv_logs.write_csv('verificacion-logs','check_maillog', f"Mensaje: Prevencion, Spam por parte de {email}, email bloqueado")
                send_csv_logs.write_log('prevencion', f'Prevencion: Spam por parte de {email}, email bloqueado"', 'Razon: Spam masivo')

        else:
            contador_email[email] = 1
            print("1")


