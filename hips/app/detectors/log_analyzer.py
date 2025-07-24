import subprocess
import re
from datetime import datetime
from collections import defaultdict
from app.utils.logger import log_alarma, log_prevencion
from app.utils.mailer import enviar_alerta_mail

DEFAULT_KEYWORDS = [
    "Failed password", "authentication failure", "sudo",
    "su: authentication failure", "session opened for user", "Accepted password"
]

ip_fallos = defaultdict(list)

def bloquear_ip(ip):
    try:
        subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        log_prevencion("Bloqueo IP", f"IP {ip} bloqueada automáticamente")
        return True
    except Exception as e:
        log_alarma("Bloqueo IP", f"Fallo al bloquear {ip}: {e}")
        return False

def extraer_timestamp(linea):
    match = re.search(r'^\w+\s+\d+\s+\d+:\d+:\d+', linea)
    if match:
        raw = match.group()
        try:
            dt = datetime.strptime(raw, "%b %d %H:%M:%S")
            return dt.replace(year=datetime.now().year).strftime('%d/%m/%Y %H:%M:%S')
        except:
            return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def extraer_ip(linea):
    match = re.search(r'from\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', linea)
    return match.group(1) if match else "localhost"

def clasificar_evento(linea):
    line_lower = linea.lower()
    if "failed password" in line_lower or "authentication failure" in line_lower:
        return "❌ Login fallido"
    elif "sudo" in line_lower and ("command" in line_lower or "session" in line_lower):
        return "⚠️ Uso de sudo"
    elif "su:" in line_lower and "authentication failure" in line_lower:
        return "🚫 Su fallido"
    elif "session opened for user root" in line_lower:
        return "⚠️ Escalada a root"
    elif "accepted password" in line_lower:
        return "✅ Login exitoso"
    else:
        return "📌 Evento autenticación"

def get_journal_logs(keywords, max_lines=1000):
    cmd = ["journalctl", "-o", "cat", "-n", str(max_lines)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        return [line for line in lines if any(k in line for k in keywords)]
    except subprocess.CalledProcessError as e:
        log_alarma("journalctl", f"Fallo al obtener logs: {e}")
        return []

def analyze_auth_logs(config=None):
    settings = config.get("settings", {}) if config else {}
    prevention = config.get("prevention", {}) if config else {}
    max_lines = settings.get("LOG_LINES", 1000)
    keywords = settings.get("AUTH_LOG_KEYWORDS", DEFAULT_KEYWORDS)
    threshold = prevention.get("LOGIN_FAIL_THRESHOLD", 5)
    bloquear_ips = prevention.get("IP_BLOCK_ENABLED", False)

    eventos = []
    logs = get_journal_logs(keywords, max_lines)

    for line in logs:
        ts = extraer_timestamp(line)
        tipo = clasificar_evento(line)
        ip = extraer_ip(line)
        mensaje = f"{ts} :: {tipo} :: IP: {ip} :: {line}"
        eventos.append(mensaje)

        if tipo in ["❌ Login fallido", "🚫 Su fallido"]:
            ip_fallos[ip].append(datetime.now())
            recientes = [t for t in ip_fallos[ip] if (datetime.now() - t).total_seconds() <= 60]
            if len(recientes) >= threshold and ip != "localhost":
                if bloquear_ips and bloquear_ip(ip):
                    alerta = f"{ts} :: IP {ip} bloqueada tras {len(recientes)} fallos :: {tipo}"
                    log_alarma("IP Bloqueada", alerta)
                    enviar_alerta_mail(config, "🚫 IP bloqueada", alerta)
                ip_fallos[ip] = []  # limpiar tras bloqueo
            else:
                log_alarma("Login fallido", mensaje)
                enviar_alerta_mail(config, f"🚨 {tipo}", mensaje)

        elif tipo in ["⚠️ Escalada a root", "⚠️ Uso de sudo"]:
            log_prevencion("Privilegios sospechosos", mensaje)
            enviar_alerta_mail(config, f"🔐 {tipo}", mensaje)
        else:
            log_prevencion("Evento de autenticación", mensaje)

    return eventos