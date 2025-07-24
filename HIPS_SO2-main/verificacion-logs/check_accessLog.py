
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
import block_ip
import send_email
import block_email
import new_password

def access_log():
    
    command = "sudo cat /var/log/httpd/access_log | grep -i 'HTTP' | grep -i '404'" 
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Verificar si hubo errores en la ejecución del comando
    contador_ip ={}
    email = ''
    if process.stdout != '':
    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
        file = process.stdout.split("\n")[:-1]
        for line in file: #analizar linea por linea del contenido obtenido en file
            ip = line.split()[0]
            print(ip)
            if ip in contador_ip: #se verifica cuantas veces aparece la ip haciendo un request del access_log
                contador_ip[ip] = contador_ip[ip] + 1
                if contador_ip[ip] == 10:
                    block_ip.block_ipf(ip)
                    send_csv_logs.write_csv('verificacion-logs','check_accessLog', f"Mensaje: Alarma, varios request http de {ip}, se procedio a bloquear la ip")
                    send_csv_logs.write_log('prevencion', 'Prevencion: Bloqueo de ip', f'Razon: Varios request de hhttp de: {ip}')
                    email = email + f"varios request http de {ip}, se procedio a bloquear la ip. \n"

            else:
                contador_ip[ip] = 1
    else:
    # Si hubo un error, imprimir el mensaje de error
        print("Error al ejecutar el comando:")
    

    if email != '':
        send_email.send_email_admin('Prevencion:', "access_log", email)

def check_messages():
    
    command = "sudo cat /var/log/message.log | grep -i 'service=smtp' | grep -i 'auth failure'" #esta seria en una version vieja de centos?
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Verificar si hubo errores en la ejecución del comando
    contador_user ={}
    email = ''
    if process.stdout != '':

    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
        file = process.stdout.split("\n")[:-1]
        for line in file:
            # Se obtiene el usuario entre corchetes [user=username]
            user = [word for word in line.split() if 'user=' in word][0]
            # Se borran los corchetes
            user = user.split('=')[-1][:-1]
            try:
                if user in contador_user:
                    contador_user[user] = contador_user[user] + 1
                    if contador_user[user] == 30:  
                        new_passwd = new_password.random_password()
                        command_new_passwd = f"echo '{user}:{new_passwd}' | sudo chpasswd"
                        subprocess.run(command_new_passwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        send_csv_logs.write_csv('verificacion-logs','check_accessLog', f"Mensaje: Prevencion, varios auth failure en /etc/log/messages del usuario {user}, se procedio al cambio de contrasena")
                        send_csv_logs.write_log('prevencion', f'Prevencion: Cambio de contrasena a {user}', 'Razon: Varios auth failure')
                        email = email + f"varios auth failure en /etc/log/message del usuario {user}, se cambio la contrasena. \n"

                else:
                    contador_user[user] = 1
            except Exception as e:
                print(f"Error:{e}")
    else:
    # Si hubo un error, imprimir el mensaje de error
        print("Error al ejecutar el comando:")
        #print(process.stderr)
    if email != '':
        send_email.send_email_admin('Prevencion:', "error de autenticacion",email )
    else:
        send_csv_logs.write_csv('verificacion-logs','check_log_messages', f"Mensaje: todo correcto")



def check_secure():
   
    command = "sudo cat /var/log/secure.log | grep -i 'smtp:auth' | grep -i 'authentication failure'" #filtro por esas strings
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    contador_user ={}
    email = ''

    # Verificar si hubo errores en la ejecución del comando
    if process.stdout != '':
    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
        file = process.stdout.split("\n")[:-1]
        for user in file:
            user = user.split('=')[-1]
            if user in contador_user:
                contador_user[user] = contador_user[user] + 1
                if contador_user[user] == 30:
                    try:
                        new_passwd = new_password.random_password()
                        command_new_passwd = f"echo '{user}:{new_passwd}' | sudo chpasswd"
                        subprocess.run(command_new_passwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        send_csv_logs.write_csv('verificacion-logs','check_accessLog', f"Mensaje: Prevencion, varios auth failure en /etc/log/secure del usuario {user}")
                        send_csv_logs.write_log('prevencion', f'Prevencion: Cambio de contrasena a {user}', 'Razon: Varios auth failure')
                        email = email + f"varios auth failure en /etc/log/secure del usuario {user}, se cambio la contrasena. \n"
                    except Exception as e:
                        print(f"Error {e}")          
            else:
                contador_user[user] = 1
            
    else:
    # Si hubo un error, imprimir el mensaje de error
        print("Error al ejecutar el comando:")
        print(process.stderr)
   
    #analizar linea por linea del contenido obtenido en file
 
    if email != '':
        send_email.send_email_admin('Prevencion:', "error de autenticacion", email )
    else:
        send_csv_logs.write_csv('verificacion-logs','check_log_messages', f"Mensaje: todo correcto")



def check_maillogg():
   
    command = "sudo cat /var/log/maillog.log | grep -i 'authid' " #filtro por authid
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    contador_email ={}
    email_admin = ''
    # Verificar si hubo errores en la ejecución del comando
    if process.stdout != '':
    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
        file = process.stdout.split("\n")[:-1]
        #analizar linea por linea del contenido obtenido en file
        for email in file:
            email = [word for word in email.split() if 'authid=' in word][0]
            email = email.split("=")[-1][:-1] # Sacamos el 'authid=' y la ',' al final. Finalmente obtenemos el email.
            if email in contador_email:
                contador_email[email] = contador_email[email] + 1
                if contador_email[email] == 30:
                    block_email.block_emailf(email)
                    send_csv_logs.write_csv('verificacion-logs','check_accessLog', f"Mensaje: Prevencion, Spam por parte de {email}, email bloqueado")
                    send_csv_logs.write_log('prevencion', f'Prevencion: Spam por parte de {email}, email bloqueado"', 'Razon: Spam masivo')
                    email_admin = email_admin + f"Spam por parte de {email}, email bloqueado. \n"
            else:
                contador_email[email] = 1
    else:
    # Si hubo un error, imprimir el mensaje de error
        print("Error al ejecutar el comando:")
        print(process.stderr)
    
   
            
    if email_admin != '':
        send_email.send_email_admin('Prevencion:', "spam masivo", email_admin)
    else:
        send_csv_logs.write_csv('verificacion-logs','check_log_messages', f"Mensaje: todo correcto")



if __name__== "__main__":
    access_log()
    check_secure()
    check_maillogg()
    check_messages()


