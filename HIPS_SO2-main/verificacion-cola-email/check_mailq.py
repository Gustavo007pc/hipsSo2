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
import send_email

def get_mail_queue_size():
    try:
        output = subprocess.check_output("mailq | tail -n 1", shell=True).decode('utf-8')
        queue_size_line = output.strip() #elimina espacios vacios de la cadena
        if queue_size_line.split()[1] == "queue" :
            queue_size = 0
            return queue_size
        else:
            queue_size = int(queue_size_line.split()[4])#separa el output para poder agarrar el numero de colas y lo pasa a int
            return queue_size
    except:
        print("Error al obtener el tamaño de la cola.")
        return -1

if __name__ == "__main__":
    queue_size = get_mail_queue_size() #trae el valor de la cola de mails
    if queue_size > 50: #verifica la cantidad
        print(f"¡Hay más de 50 mensajes en cola! ({queue_size} mensajes)")
        send_csv_logs.write_csv('verificacion-cola-email','check_mailq', f"Mensaje: Alerta, hay una gran cola de email, tamano:{queue_size}")
        send_csv_logs.write_log('alarmas', 'Alerta: Seguridad del correo electronico', 'Razon: Cola alta de emails')
        send_email.send_email_admin('Alarma:', "Correo", f"La cola de emails es muy grande, tamano de {queue_size}")


    else:
        print(f"El tamaño de la cola es de {queue_size} mensajes.")
        send_csv_logs.write_csv('verificacion-cola-email', 'check_mailq', f"Mensaje: Hay una cola de {queue_size}")