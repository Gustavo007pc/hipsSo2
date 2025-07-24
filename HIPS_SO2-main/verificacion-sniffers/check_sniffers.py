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
import kill_ps
import send_email

def check_sniffers_promiscuos():
    #Se verifica si actualmente esta activo el dispositivo en modo promiscuo
    command = "sudo ip a show enp0s3 | grep -i 'promis'"
    file = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(file)
    #Si es cero es que la palabra promis se encuentra en el archivo
    if file.stdout != '': 
        print("Hay dispositivos en modo promiscuo")
        send_csv_logs.write_csv('verificacion-sniffers','check_sniffers', "Mensaje: Alerta, dispositivo en modo promiscuo")
        send_csv_logs.write_log('alarmas', f'Alerta: Posible sniffer', 'Razon: modo promiscuo activado')
        send_email.send_email_admin('Alarma', "Modificacion archivos binarios", "/etc/shadow ha sido modificado")
    else:
        print("No hay dispositivos en modo promiscuo")
        send_csv_logs.write_csv('verificacion-sniffers','check_sniffers', "Mensaje: No hay dispositivos en modo promiscuo")
    #Se verifica en /var/log/messages si se entro y salio del modo promiscuo en algun momento
    command1 = "sudo cat /var/log/messages |grep -i entered | grep -i promis"
    command2 = "sudo cat /var/log/messages |grep -i left | grep -i promis"
    file_entered = subprocess.run(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    file_left = subprocess.run(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    dic1 = {"Mensaje": "Entro en modo promiscuo"}
    dic2 = {"Mensaje": "Salio de modo promiscuo"}
    if file_entered.stdout != '':
        file_entered = file_entered.stdout.split('\n')[:-1]
        #Se guarda la informacion del momento en el que se entro en modo promiscuo
        for line1 in file_entered:
            line1 = line1.split()
            dic1["Mes"] = line1[0]
            dic1["Dia"] = line1[1]
            dic1["Hora"] = line1[2]
        print(dic1)
        send_csv_logs.write_csv('verificacion-sniffers','check_sniffers', dic1)

        
    else:
        print("No se entro en modo promiscuo")
    if file_left.stdout != '':
        file_left = file_left.stdout.split('\n')[:-1]
        #Se guarda la informacion del momento en que salio del modo promiscuo
        for line2 in file_left:
            line2 = line2.split()
            dic2["Mes"] = line2[0]
            dic2["Dia"] = line2[1]
            dic2["Hora"] = line2[2]
        print(dic2)
        send_csv_logs.write_csv('verificacion-sniffers','check_sniffers', dic2)
# Busca si las herramientas que estan en la lista de sniffers se estan ejecutando
def check_sniffers_apps():
    known_sniffers = ["tcpdump", "tshark", "wireshark", "hola"]
    sniffers_in_execution = []
    email = ''
    for sniffer in known_sniffers:
        comando = f"ps -aux | grep {sniffer} | grep -v grep |  awk '{{print $1, $2, $NF}}'" # se buscan los parametros deseados entre ellos el pid
        resultado = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(resultado.stdout)
        if resultado.stdout != '':
            print(f'Se ha encontrado el proceso {sniffer} en ejecución.')
            sniffers_in_execution.append(sniffer)
            for line in resultado.stdout.splitlines(): # se separa la cadena para iterar sobre los ouputs de reultado
                pid = line.split()[1] #Esta es la ubicacion del pid
                print(pid)
                kill_ps.kill_process(pid) #Se mata al proceso
                send_csv_logs.write_csv('verificacion-sniffers','check_sniffers', f"Mensaje: Prevencion, {sniffer} en ejecucion, se mato el proceso pid:{pid}")
                send_csv_logs.write_log('prevencion', f'Alerta: posible sniffer', f'Razon: {sniffer} en ejecucion, se mato el proceso pid:{pid}')
                email = email + f"{sniffer} en ejecucion, se mato el proceso pid:{pid}\n"

            
        else:
            print(f"No se ha encontrado ningun proceso de'{sniffer}'.")
    if resultado.stdout != '':
        send_email.send_email_admin('Prevencion:', "posibles sniffers", email)
    


check_sniffers_promiscuos()
check_sniffers_apps()