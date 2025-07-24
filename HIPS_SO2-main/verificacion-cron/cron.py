import os
import pwd
from crontab import CronTab
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

def listar_tareas_cron():
    usuarios = pwd.getpwall() #trae todo el contenido de /etc/passwd
    email = ''
    print("Tareas cron de todos los usuarios:\n")
    #print(usuarios)
    for usuario in usuarios:
        usuario_actual = usuario.pw_name #filtra los usuarios obtenidos de /etc/passwd
        #print(usuario_actual)
        archivo_cron = f"/var/spool/cron/{usuario_actual}"
        
        if not os.path.isfile(archivo_cron):
            # Si el usuario no tiene un archivo cron, pasamos al siguiente.
            #send_csv_logs.write_csv('verificacion-cron','cron', f"Mensaje: Usuario: {usuario_actual} no tiene un archivo en /var/spool/cron/{usuario_actual}")
            continue
        
        cron = CronTab(user=usuario_actual)
        send_csv_logs.write_csv('verificacion-cron','cron', f"Mensaje: Usuario: {usuario_actual} tiene un archivo en /var/spool/cron/{usuario_actual}")
        send_csv_logs.write_log('alarmas', f'Alerta: Usuario: {usuario_actual} tiene un archivo en /var/spool/cron/{usuario_actual} ', 'Razon: archivo cron ejecutandose')
        email = email + f"Usuario: {usuario_actual} tiene un archivo en /var/spool/cron/{usuario_actual}"
        print(f"Usuario: {usuario_actual}")
        for tarea in cron:
            print(f"Comando: {tarea.command}")
            print(f"Frecuencia: {tarea.frequency_per_hour()} veces por hora.")
            print()
    if email != '':
        send_email.send_email_admin('Alerta:', "cron encontrado", email)
    else:
        send_csv_logs.write_csv('verificacion-cron','cron', f"Mensaje: Todo correcto")

        

listar_tareas_cron()