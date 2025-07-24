import subprocess

def kill_process(pid):
    try:
        subprocess.run(["sudo", "kill", "-9", str(pid)])
        print(f"Proceso {pid} terminado.")
    except:
        print(f"Error al matar el proceso {pid}. Ya ha sido terminado o no existe.")