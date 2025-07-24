import os
from app.utils.logger import log_alarma

def detect_uid0_processes():
    uid0_processes = []

    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                status_path = f"/proc/{pid}/status"
                with open(status_path, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    if line.startswith("Uid:"):
                        uid = int(line.split()[1])
                        if uid == 0:
                            uid0_processes.append(pid)
            except Exception:
                continue

    if len(uid0_processes) > 1:
        mensaje = f"UID 0 usado por múltiples procesos: {', '.join(uid0_processes)}"
        log_alarma("Usuarios conectados", mensaje)
        return [mensaje]

    return []
