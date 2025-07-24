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


def check_ddos():
    
    command = "sudo cat /var/log/dns-tcpdump/ataque" 
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
   
    contador_ip ={}
    email =''

    #analizar linea por linea del contenido obtenido en file
    # Dividir la salida en líneas y eliminar el último elemento (línea vacía)
    if process.stdout != '':
        file = process.stdout.split("\n")[:-1]
        for line in file:
            ip_o = line.split()[2]
            ip_d = line.split()[4][:-1]
            if (ip_o , ip_d) in contador_ip: #se verifica cuantas veces aparece la ip_o ataca a ip_d
                contador_ip[(ip_o , ip_d)] = contador_ip[(ip_o , ip_d)] + 1
            else:
                contador_ip[(ip_o , ip_d)] = 1

        for (ip_o,ip_d), ocurrencia in contador_ip.items():
            if ocurrencia >= 5:
                print(ocurrencia)
                block_ip.block_ipf(ip_o)
                send_csv_logs.write_csv('verificacion-ddos','check_log_ddos', f"Mensaje: Prevencion, ip bloqueada por ataque ddos, ip:{ip_o}")
                send_csv_logs.write_log('prevencion', 'Prevencion: bloquear', 'Razon: ataque dns',f'ip bloqueada por ataque ddos, ip:{ip_o}' )
                email = email + f'ip bloqueada por ataque ddos, ip:{ip_o}\n'

    if email != '':
        send_email.send_email_admin('Prevencion:', "ataque ddos", email)
    else:
        send_csv_logs.write_csv('verificacion-ddos','check_log_ddos', f"Mensaje: Todo correcto, no hay ataques ddos desde una ip")

        
        
            
check_ddos()
