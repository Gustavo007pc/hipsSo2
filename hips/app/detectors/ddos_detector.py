import re
import subprocess
from collections import defaultdict
from datetime import datetime
import psutil
from app.utils.logger import log_alarma, log_prevencion

# Ruta de log para eventos DNS
DNS_LOG = "/var/log/dns_attack.log"

# Expresión regular para extraer IPs
IP_PATTERN = re.compile(r'from\s+(\d+\.\d+\.\d+\.\d+)')

DNS_PORT = 53  # puerto UDP/TCP usado por DNS

def parse_dns_log():
    """
    Lee DNS_LOG y devuelve un dict: { ip: [datetime1, datetime2, ...] }
    """
    ip_times = defaultdict(list)
    try:
        with open(DNS_LOG, 'r') as f:
            for line in f:
                match = IP_PATTERN.search(line)
                if not match:
                    continue
                ip = match.group(1)

                # Parsear fecha (formato tipo: Jul 24 12:34:56)
                try:
                    date_str = " ".join(line.split()[:3])
                    dt = datetime.strptime(date_str, "%b %d %H:%M:%S")
                    dt = dt.replace(year=datetime.now().year)
                except Exception:
                    dt = datetime.now()
                ip_times[ip].append(dt)
    except FileNotFoundError:
        log_alarma("DDOS DNS", f"Archivo de log no encontrado: {DNS_LOG}")
    except Exception as e:
        log_alarma("DDOS DNS", f"Error leyendo {DNS_LOG}: {e}")
    return ip_times

def detect_ddos_from_logs(config):
    """
    Analiza el log DNS y bloquea IPs que excedan MAX_REQUESTS en TIME_WINDOW.
    Devuelve lista de alertas generadas.
    """
    alerts = []
    ip_times = parse_dns_log()
    now_ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    MAX_REQUESTS = config["settings"].get("MAX_REQUESTS", 100)
    TIME_WINDOW = config["settings"].get("TIME_WINDOW", 60)

    for ip, times in ip_times.items():
        times.sort()
        for i in range(len(times)):
            count = 1
            for j in range(i + 1, len(times)):
                if (times[j] - times[i]).total_seconds() <= TIME_WINDOW:
                    count += 1
                else:
                    break
            if count > MAX_REQUESTS:
                alert = (
                    f"{now_ts} :: DDOS detectado en DNS desde IP {ip} "
                    f"({count} req en ≤ {TIME_WINDOW}s)"
                )
                alerts.append(alert)
                log_prevencion("DDOS DNS (log)", alert)
                _prevent_ddos_ip(ip)
                break
    return alerts

def _prevent_ddos_ip(ip):
    """
    Usa iptables para bloquear el origen de DDOS.
    """
    try:
        subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )
        log_prevencion("Bloqueo DDOS", f"IP {ip} bloqueada en firewall")
    except subprocess.CalledProcessError as e:
        log_alarma("DDOS DNS", f"Fallo bloqueando IP {ip}: {e}")

def detect_ddos_from_connections(config):
    """
    Cuenta conexiones activas al puerto DNS. Si excede CONN_THRESHOLD, genera alerta.
    """
    alerts = []
    conns = psutil.net_connections(kind='inet')
    dns_conns = [
        c for c in conns
        if (c.laddr and c.laddr.port == DNS_PORT)
           or (c.raddr and c.raddr.port == DNS_PORT)
    ]
    count = len(dns_conns)
    CONN_THRESHOLD = config["settings"].get("CONN_THRESHOLD", 200)

    if count > CONN_THRESHOLD:
        ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        msg = f"{ts} :: {count} conexiones DNS activas (> {CONN_THRESHOLD})"
        alerts.append(msg)
        log_prevencion("DDOS DNS (conn)", msg)
    return alerts

def detect_ddos(config):
    """
    Ejecuta ambas detecciones DDOS: por logs y por conexiones.
    """
    alerts = []
    alerts.extend(detect_ddos_from_logs(config))
    alerts.extend(detect_ddos_from_connections(config))
    return alerts

if __name__ == "__main__":
    import json
    try:
        with open("config.json") as f:
            config = json.load(f)
    except:
        config = {
            "settings": {
                "MAX_REQUESTS": 100,
                "TIME_WINDOW": 60,
                "CONN_THRESHOLD": 200
            }
        }

    for alerta in detect_ddos(config):
        print(alerta)