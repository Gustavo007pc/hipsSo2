import psutil
from datetime import datetime
from app.utils.logger import log_alarma
from app.utils.process_killer import kill_process_by_pid

# Umbrales (pueden pasarse desde config más adelante)
RAM_THRESHOLD_MB = 100
CPU_THRESHOLD_PERCENT = 20

def check_high_resource_processes(kill_enabled=False):
    alerts = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            cpu_percent = proc.info['cpu_percent']

            if mem_mb > RAM_THRESHOLD_MB or cpu_percent > CPU_THRESHOLD_PERCENT:
                alert = (f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} :: "
                         f"Proceso con alto consumo: {proc.info['name']} "
                         f"(PID: {proc.info['pid']}, RAM: {mem_mb:.2f}MB, CPU: {cpu_percent:.2f}%)")
                print(alert)
                log_alarma("Alto consumo de recursos", alert)
                alerts.append(alert)

                if kill_enabled:
                    if kill_process_by_pid(proc.info['pid']):
                        print(f"→ Proceso {proc.info['name']} (PID {proc.info['pid']}) eliminado.")
                    else:
                        print(f"→ No se pudo eliminar el proceso {proc.info['name']}.")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return alerts
