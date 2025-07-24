import subprocess
import sys
import os

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

def verificar_ssh_logs():
    command = "sudo cat /var/log/secure.log | grep -i 'sshd' | grep -i 'Failed password'"
    email = ''
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("hola")
        print(result.returncode)
        if result.stdout == '':
            send_csv_logs.write_csv('verificacion-ssh','check_ssh_logs', f"Mensaje: Todo correcto, no hay intentos de acceso al sistema")
        else:
            ssh_passwdf = result.stdout.split('\n')[:-1]  # Eliminamos el ultimo elemento vacio
            print(ssh_passwdf)
    except:
        print("error")

    ip_contador = {} #diccionario que se utilizara como contador para las ips
    if result.stdout != '':
        for element_line in ssh_passwdf:
            ip_origen = element_line.split()[-4] #En esa posicion se encuentra la ip luego de hacer el split
            if ip_origen in ip_contador:
                ip_contador[ip_origen]= ip_contador[ip_origen] + 1
            
            else:
                ip_contador[ip_origen]=1
        for ip, ocurrencia in ip_contador.items():  #se separan en (ip_origen, valor )
            if ocurrencia >= 5:
                send_csv_logs.write_csv('verificacion-ssh','check_ssh_logs', f"Mensaje: Alarma, intento de conexion remota (ssh) de {ip}")
                send_csv_logs.write_log('prevencion', 'Prevencion: Bloqueo de ip', f'Razon: Varios intentos de acceso al sistema de {ip}')
                block_ip.block_ipf(ip)
                email = email + f'Razon: Varios intentos de acceso al sistema de {ip}, se procedio a bloquear la ip'
    if email != '':
        send_email.send_email_admin('Prevencion:', "intento de intrusion", email)


verificar_ssh_logs()

