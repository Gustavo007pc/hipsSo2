import subprocess
import random
import string 
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
import new_password
#Genera una contrasena random

def check_secure():
   
    command = "sudo cat /var/log/secure.log | grep -i 'smtp:auth' | grep -i 'authentication failure'" #filtro por esas strings
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
    
    contador_user ={}

    #analizar linea por linea del contenido obtenido en file
    for user in file:
        user = user.split('=')[-1]
        if user in contador_user:
            contador_user[user] = contador_user[user] + 1
            if contador_user[user] == 30:
                '''new_passwd = new_password.random_password()
                command_new_passwd = f"echo '{user}:{new_passwd}' | sudo chpasswd"
                subprocess.run(command_new_passwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)'''
                send_csv_logs.write_csv('verificacion-logs','check_log_secure', f"Mensaje: Prevencion, varios auth failure en /etc/log/secure del usuario {user}")
                send_csv_logs.write_log('prevencion', f'Prevencion: Cambio de contrasena a {user}', 'Razon: Varios auth failure')

        else:
            contador_user[user] = 1
            print("1")


