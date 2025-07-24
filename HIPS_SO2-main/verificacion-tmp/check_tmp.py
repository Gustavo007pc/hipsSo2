import os
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

def check_tmpf():
    # Comprueba si la carpeta de cuarentena existe
    cuarentena_dir = "/quarentine/tmp_scripts"
    if not os.path.exists(cuarentena_dir):
        os.makedirs(cuarentena_dir)

    command = "sudo find /tmp -type f 2>/dev/null"
    file_tmp = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    files_list = file_tmp.stdout.splitlines()
    print(files_list)
    email_body = ''
    archivos_cuarentena = []

    for file_list in files_list:
        cuarentena = {}

        # Verifica si el archivo es de tipo sospechoso
        if any(substring in file_list for substring in [".cpp", ".c", ".py", ".sh", ".php"]):
            cuarentena['ruta_del_archivo'] = file_list
            cuarentena['destino_cuarentena'] = os.path.join(cuarentena_dir, os.path.basename(file_list).replace("/", "-"))
            cuarentena['razon'] = "Archivo sospechoso"
            archivos_cuarentena.append(cuarentena)
        else:  #Busca si el archivo tiene un #! en la primera línea, por si hay un archivo script
            try:
                with open(file_list, "r") as f:
                    primera_linea = f.readline()  # Se lee la primera línea del archivo
                    if "#!" in primera_linea:
                        cuarentena['ruta_del_archivo'] = file_list
                        cuarentena['destino_cuarentena'] = os.path.join(cuarentena_dir, os.path.basename(file_list).replace("/", "-"))
                        cuarentena['razon'] = "Archivo sospechoso de tipo #!"
                        archivos_cuarentena.append(cuarentena)
            except Exception:
                print(f"El archivo {file_list} está codificado en bytes")

    for archivo in archivos_cuarentena:
        try:
            # Verifica si el archivo ya existe en la carpeta de cuarentena 
            if not os.path.exists(archivo['destino_cuarentena']):
                command = f"sudo mv {archivo['ruta_del_archivo']} {archivo['destino_cuarentena']}"
                subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                send_csv_logs.write_csv('verificacion-tmp','check_tmp', f"Mensaje: Prevencion, {archivo}: archivo sospechoso en /tmp, se movio a cuarentena /quarentine")
                send_csv_logs.write_log('prevencion', f'Prevencion: archivo sospechoso {archivo} en /tmp, se movio a cuarentena /quarentine', 'Razon: extension sospechosa')
                email_body = email_body + f'\nPrevencion: archivo sospechoso {archivo} en /tmp, se movio a cuarentena /quarentine', 'Razon: extension sospechosa\n'
                
            else:
                print(f"El archivo {archivo['ruta_del_archivo']} ya existe en la carpeta de cuarentena.")
                send_csv_logs.write_csv('verificacion-tmp','check_tmp', f"El archivo {archivo['ruta_del_archivo']} ya existe en la carpeta de cuarentena.")
        except:
            print(f"No se pudo mover a cuarentena el archivo: {archivo['ruta_del_archivo']}.")

    
    #Procedemos a escribir en el archivo
    if archivos_cuarentena:    
        mensaje = "Ya se movio los ultimos archivos"
        print("hola")
        send_email.send_email_admin('Prevencion: ', "Scripts en /tmp", email_body)
    else:
        send_csv_logs.write_csv('verificacion-tmp','check_tmp', f"Ningun archivo sospechoso en /tmp")

check_tmpf()
