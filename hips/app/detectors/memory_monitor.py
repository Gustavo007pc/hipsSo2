# app/detectors/memory_monitor.py

import psutil
import time
from datetime import datetime
from app.utils.logger import log_prevencion

# ─── Configuración ─────────────────────────────────────────────────────────────
TEST_MODE           = True                           # True = 15s de seguimiento, False = 5min
MEMORY_THRESHOLD_MB = 900                            # MB
TIME_THRESHOLD_SEC  = 15 if TEST_MODE else 300       # Segundos antes de kill
INTERVAL_SEC        = 5                              # Pausa entre escaneos

# El script que queremos controlar
SAFE_TARGET = ""
# "test_memory_bomb.py"

# Procesos esenciales que NUNCA terminamos
WHITELIST = {
    "Xorg", "init", "systemd", "sshd", "bash", "gnome-shell, code"
}

# Estado interno: pid -> timestamp de primera detección
high_mem_procs = {}

def bytes_to_mb(b):
    return b / (1024 * 1024)

def check_memory_usage():
    """
    Corre un bucle de escaneos cada INTERVAL_SEC durante TIME_THRESHOLD_SEC.
    Inicia seguimiento al primer umbral, espera TIME_THRESHOLD_SEC y mata SOLO
    a SAFE_TARGET si supera MEMORY_THRESHOLD_MB.
    """
    alerts = []
    loops = int(TIME_THRESHOLD_SEC / INTERVAL_SEC) + 1

    for cycle in range(loops):
        now = datetime.now()

        for proc in psutil.process_iter(['pid','name','memory_info','cmdline']):
            try:
                pid     = proc.info['pid']
                name    = proc.info['name']
                mem_mb  = bytes_to_mb(proc.info['memory_info'].rss)
                cmdline = " ".join(proc.info.get('cmdline', []))

                # 1) Excluir demonios o procesos críticos
                if name in WHITELIST:
                    continue

                # 2) Solo procesar tu script de prueba
                if SAFE_TARGET not in cmdline:
                    continue

                # 3) Iniciar seguimiento
                if mem_mb > MEMORY_THRESHOLD_MB and pid not in high_mem_procs:
                    high_mem_procs[pid] = now
                    msg = f"{name} (PID {pid}) detectado con {mem_mb:.1f} MB"
                    log_prevencion("Seguimiento RAM", msg)
                    print(f"🧠   {msg}")

                # 4) Ya en seguimiento: revisar elapsed
                elif pid in high_mem_procs and mem_mb > MEMORY_THRESHOLD_MB:
                    elapsed = (now - high_mem_procs[pid]).total_seconds()
                    print(f"⏱️   {name} (PID {pid}) lleva {elapsed:.1f}s con {mem_mb:.1f} MB")

                    if elapsed >= TIME_THRESHOLD_SEC:
                        alerta = (
                            f"{now.strftime('%d/%m/%Y %H:%M:%S')} :: "
                            f"Proceso {name} (PID {pid}) eliminado por "
                            f"{mem_mb:.1f} MB durante {elapsed:.0f}s"
                        )
                        alerts.append(alerta)
                        log_prevencion("Proceso terminado por RAM", alerta)
                        print(f"💥   {alerta}")

                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()

                        del high_mem_procs[pid]

                # 5) Cancelar seguimiento si baja del umbral
                elif pid in high_mem_procs and mem_mb <= MEMORY_THRESHOLD_MB:
                    msg = f"{name} (PID {pid}) bajó a {mem_mb:.1f} MB → seguimiento cancelado"
                    log_prevencion("Normalizado RAM", msg)
                    print(f"✔️   {msg}")
                    del high_mem_procs[pid]

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                high_mem_procs.pop(pid, None)

        # Pausa antes de siguiente ciclo (salvo último)
        if cycle < loops - 1:
            time.sleep(INTERVAL_SEC)

    return alerts