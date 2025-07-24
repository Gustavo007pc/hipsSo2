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

def check_messages():
    
    command = "sudo cat /var/log/message.log | grep -i 'service=smtp' | grep -i 'auth failure'" #esta seria en una version vieja de centos?
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Verificar si hubo errores en la ejecución del comando
    if process.returncode == 0:
    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
        file = process.stdout.split("\n")[:-1]
        print(file)
    else:
    # Si hubo un error, imprimir el mensaje de error
        print("Error al ejecutar el comando:")
        #print(process.stderr)
    
    contador_user ={}

    #analizar linea por linea del contenido obtenido en file
    for line in file:
        # Se obtiene el usuario entre corchetes [user=username]
        user = [word for word in line.split() if 'user=' in word][0]
         # Se borran los corchetes
        user = user.split('=')[-1][:-1]
        print(user) 
        try:
            if user in contador_user:
                contador_user[user] = contador_user[user] + 1
                if contador_user[user] == 30:  
                    #new_passwd = new_password.random_password()
                    #command_new_passwd = f"echo '{user}:{new_passwd}' | sudo chpasswd"
                    #subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    send_csv_logs.write_csv('verificacion-logs','check_log_messages', f"Mensaje: Prevencion, varios auth failure en /etc/log/messages del usuario {user}, se procedio al cambio de contrasena")
                    send_csv_logs.write_log('prevencion', f'Prevencion: Cambio de contrasena a {user}', 'Razon: Varios auth failure')

            else:
                contador_user[user] = 1
        except Exception as e:
            print(f"Error:{e}")
            


