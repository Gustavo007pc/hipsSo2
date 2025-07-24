import subprocess
import os
import sys
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
# trae los procesos que mas consumen de cpu y ram con el comando ps
def get_highest_process(mem_or_cpu):
    high_consume = f"ps -eo pid,%mem,%cpu --sort=-%{mem_or_cpu} | head -n 20"
    process_c = subprocess.run(high_consume, shell=True, capture_output=True, text=True)
    process_lines = process_c.stdout.split("\n")[1:][:-1]
    print(process_lines)
    process_list = []

    for process_line in process_lines:
        proc = process_line.split()
        # Diccionario para guardar la información del proceso
        process = {
            "PID": int(proc[0]),
            "%MEM": float(proc[1]),
            "%CPU": float(proc[2])
        }

        execution_time_c = f"ps -o etime= -p {process['PID']}"  # Tiempo de ejecución del proceso
        execution_time = subprocess.run(execution_time_c, shell=True, capture_output=True, text=True)
        execution_time = execution_time.stdout.strip()

        # Verifica si el resultado contiene "ELAPSED"
        if "ELAPSED" in execution_time:
            # Omitir este proceso ya que el tiempo de ejecución no pudo obtenerse correctamente
            print(f"Error al obtener el tiempo de ejecución para el proceso PID {process['PID']}.")
            continue

        # Obtener el tiempo en minutos
        time_parts = execution_time.split(":")
        try:
            if len(time_parts) == 3:  # si tiene hora, minutos y segundos.
                execution_time = float(time_parts[0]) * 60 + float(time_parts[1]) + float(time_parts[2])/60.0
            else:
                execution_time = float(time_parts[0]) + float(time_parts[1])/60.0
        except ValueError:
            print(f"Error al convertir el tiempo de ejecución para el proceso PID {process['PID']}.")
            continue

        # Se agrega el tiempo de ejecución a la lista de procesos de alto consumo
        process["Tiempo de Ejecucion"] = execution_time
        process_list.append(process)

    return process_list

def verificar_procesos_cpu_ram():
    highest_mem = get_highest_process("mem")
    highest_cpu = get_highest_process("cpu")
    kill_list = []
    email = ''
    for process in highest_mem:
        # Si se usa más del 80% de la memoria RAM
        if process["%MEM"] > 80.0:    
            process["motivo"] = "usa mucha memoria"
    
            if(process["Tiempo de Ejecucion"]) > 1:
                kill_list.append(process)
                send_csv_logs.write_csv('verificacion-consumo', 'check_uso_alto', f"Prevencion, el proceso: {process['PID']} consume mucha memoria, el proceso ha sido matado")
                send_csv_logs.write_log('alarmas', 'Alarma: Sistema saturado', f"Razon: Uso de mucha memoria de {process['PID']}") 
                send_csv_logs.write_log('prevencion', f'Prevencion: Matar proceso {process["PID"]}', 'Razon: Uso de mucha memoria') 
                email=email + f"Prevencion, el proceso: {process['PID']} consume mucha memoria, se ha eliminado\n" 
                     

    for process in highest_cpu:
        # Si se usa más del 80% del CPU
        if process["%CPU"] > 80.0:
            process["motivo"] = "usa mucha CPU"
            print(process["Tiempo de Ejecucion"])
            if (process["Tiempo de Ejecucion"]) > 1:
                send_csv_logs.write_csv('verificacion-consumo', 'check_uso_alto', f"Prevencion, el proceso: {process['PID']} consume mucha CPU, el proceso ha sido matado.")
                send_csv_logs.write_log('alarmas', 'Alarma: Sistema saturado', f"Razon: Uso de mucha CPU de {process['PID']}") 
                send_csv_logs.write_log('prevencion', f'Prevencion: Matar proceso {process["PID"]}', 'Razon: Uso de mucha CPU') 
                kill_list.append(process)
                email=email + f"Prevencion, el proceso: {process['PID']} consume mucha cpu, se ha eliminado\n" 

    # Procedemos a matar los procesos que abusaron de los recursos
    for process in kill_list:
        kill_ps.kill_process(process["PID"])
    if kill_list:
        send_email.send_email_admin('Prevencion:', "alto consumo de ram", email)


if __name__ == "__main__":
    verificar_procesos_cpu_ram()
