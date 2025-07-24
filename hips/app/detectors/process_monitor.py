import subprocess
from datetime import datetime
import re

from app.utils.logger import log_alarma
from app.utils.registrar_prevencion import registrar_prevencion

# Procesos comúnmente usados en ataques, escaneo o post-explotación
SUSPICIOUS_PROCESSES = [
    "nc", "ncat", "netcat", "tcpdump", "wireshark", "metasploit", "hydra",
    "john", "sqlmap", "msfconsole", "powershell", "bash", "sh", "python", "perl"
]

def check_suspicious_processes(whitelist, config=None):
    """
    Escanea procesos activos y detecta procesos sospechosos que NO estén en la whitelist.
    Si AUTOKILL_PROCESSES está activo en config, elimina el proceso automáticamente.
    Devuelve lista de alertas y PIDs detectados.
    """
    alerts = []
    suspicious_pids = []
    autokill = False

    if config:
        autokill = config.get("prevention", {}).get("AUTOKILL_PROCESSES", False)

    try:
        ps_output = subprocess.check_output(["ps", "aux"], text=True)
        lines = ps_output.strip().split('\n')[1:]  # Ignorar encabezado

        for line in lines:
            if any(proc in line for proc in whitelist):
                continue

            for target in SUSPICIOUS_PROCESSES:
                if re.search(rf'\b{re.escape(target)}\b', line):
                    parts = line.split()
                    pid = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1
                    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    alert = f"{timestamp} :: Proceso sospechoso detectado: {target} (PID {pid}) :: localhost"

                    alerts.append(alert)
                    suspicious_pids.append(pid)
                    log_alarma("Proceso sospechoso", alert)

                    registrar_prevencion(config, f"Proceso sospechoso: {target} (PID {pid})", origen="localhost", modulo="process_monitor")

                    if autokill and pid > 0:
                        try:
                            subprocess.run(["kill", "-9", str(pid)], check=True)
                            accion = f"Proceso {target} (PID {pid}) eliminado automáticamente"
                            registrar_prevencion(config, accion, origen="localhost", modulo="process_monitor")
                        except Exception as e:
                            log_alarma("Error al eliminar proceso", f"{target} → {e}")
                    break  # evitar múltiples alertas para misma línea

    except Exception as e:
        error = f"[ERROR] Escaneo de procesos falló: {str(e)}"
        alerts.append(error)
        log_alarma("Process Monitor", error)

    return alerts, suspicious_pids