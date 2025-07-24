import os
import subprocess
from app.utils.logger import log_alert

def check_sniffers():
    alerts = []

    # Verificar si alguna interfaz está en modo promiscuo
    try:
        output = subprocess.check_output("ip link", shell=True).decode()
        for line in output.splitlines():
            if "PROMISC" in line:
                interface = line.split(":")[1].strip()
                msg = f"Interfaz en modo promiscuo detectada: {interface}"
                alerts.append(msg)
                log_alert("Modo promiscuo", msg)
    except Exception as e:
        log_alert("Error al verificar modo promiscuo", str(e))

    # Buscar procesos relacionados a sniffers comunes (tcpdump, wireshark, etc.)
    sniffers_binarios = ["tcpdump", "wireshark", "ettercap", "dsniff", "ngrep", "snort"]
    try:
        output = subprocess.check_output("ps aux", shell=True).decode()
        for line in output.splitlines():
            for binario in sniffers_binarios:
                if binario in line and "grep" not in line:
                    msg = f"Proceso sniffer detectado: {line}"
                    alerts.append(msg)
                    log_alert("Sniffer detectado", msg)
                    break
    except Exception as e:
        log_alert("Error al buscar procesos sniffers", str(e))

    return alerts
