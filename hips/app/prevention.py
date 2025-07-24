# app/prevention.py

import subprocess
from app.utils.logger import log_alarma

def kill_process_by_name(proc_name):
    """
    Termina todos los procesos que coincidan con proc_name.
    Registra en log y devuelve mensaje con resultado.
    """
    try:
        # Buscar PIDs con pgrep -f (busca por nombre completo o parte)
        pids = subprocess.check_output(["pgrep", "-f", proc_name], text=True).split()
        if not pids:
            return f"No se encontraron procesos '{proc_name}' para terminar."

        for pid in pids:
            subprocess.run(["kill", "-9", pid])
            log_alarma("Prevención", f"Proceso {proc_name} (PID {pid}) terminado")
        
        return f"Procesos '{proc_name}' terminados: {', '.join(pids)}"
    
    except subprocess.CalledProcessError:
        # pgrep no encontró procesos
        return f"No se encontraron procesos '{proc_name}' para terminar."
    except Exception as e:
        return f"Error al terminar procesos '{proc_name}': {e}"
