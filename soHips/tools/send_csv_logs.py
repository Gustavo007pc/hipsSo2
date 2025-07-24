import csv
from datetime import datetime
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


# Escribe un registro de una alerta o prevencion
# En /var/log/hips/alarmas.log o /var/log/hips/prevencion.log
# Formato fecha_hora :: tipo_alarma :: ip_email   motivo

def write_log(alarmas_o_prevencion, tipo_alarma, reason, ip_or_email = ''):
    try:
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        text = f'{date} :: {tipo_alarma} :: {ip_or_email} \t{reason}'

        if alarmas_o_prevencion == 'alarmas' or alarmas_o_prevencion == 'prevencion':
            os.system(f"sudo echo '{text}' >> /var/log/hips/{alarmas_o_prevencion}.log")
        else:
            print("Error input")
    except Exception as e:
        print(f"Error al escribir log: {e}")
        



def write_csv(file, file_name, message):
    try:
        date=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        with open(f"/var/log/hips/output/{file}/{file_name}.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, message])
        print("Guardado exitoso en .csv")
    except Exception as e:
        print(f"Error al guardar .csv {e}")

