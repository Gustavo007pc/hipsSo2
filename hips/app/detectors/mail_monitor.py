import re
import subprocess
from collections import defaultdict
from datetime import datetime
from app.utils.logger import log_alarma, log_prevencion
from app.utils.mailer import enviar_alerta_mail

# Remitentes bloqueados simuladamente
remitentes_suspendidos = set()

def get_postfix_logs():
    """Extrae los logs recientes del servicio Postfix"""
    try:
        result = subprocess.run(
            ["journalctl", "-u", "postfix", "--no-pager", "--since", "today"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )
        if result.returncode != 0:
            log_alarma("Postfix", f"Error al obtener logs: {result.stderr.strip()}")
            return []
        return result.stdout.splitlines()
    except Exception as e:
        log_alarma("Postfix", f"Excepción en journalctl: {e}")
        return []

def parse_postfix_logs():
    """
    Parsea los logs y extrae los timestamps por remitente.
    Retorna dict: { remitente : [datetime1, datetime2, ...] }
    """
    patron_remitente = re.compile(r"from=<([^>]+)>")
    user_times = defaultdict(list)

    for line in get_postfix_logs():
        match = patron_remitente.search(line)
        if not match:
            continue

        sender = match.group(1)
        try:
            # Extraer fecha: Ej. Jul 24 04:02:01
            partes = line.strip().split()
            date_str = " ".join(partes[:3])
            dt = datetime.strptime(date_str, "%b %d %H:%M:%S")
            dt = dt.replace(year=datetime.now().year)
            user_times[sender].append(dt)
        except Exception:
            continue

    return user_times

def detect_mass_mailing(config):
    """
    Detecta envío masivo por remitente según config.
    Retorna lista de alertas si se supera el umbral.
    """
    alerts = []
    settings = config.get("settings", {})
    prevention = config.get("prevention", {})
    MAX_MAILS = settings.get("MAX_MAILS", 10)
    TIME_WINDOW = settings.get("MAIL_TIME_WINDOW", 60)
    bloquear_spammers = prevention.get("BLOCK_SPAMMERS", False)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    user_times = parse_postfix_logs()

    for sender, timestamps in user_times.items():
        sorted_times = sorted(timestamps)

        for i in range(len(sorted_times)):
            count = 1
            for j in range(i + 1, len(sorted_times)):
                delta = (sorted_times[j] - sorted_times[i]).total_seconds()
                if delta <= TIME_WINDOW:
                    count += 1
                else:
                    break

            if count > MAX_MAILS:
                alerta = f"{now} :: Envío masivo detectado para {sender} :: {count} mails en ≤ {TIME_WINDOW}s"
                alerts.append(alerta)
                log_alarma("Spam detectado", alerta)
                log_prevencion("Remitente sospechoso", f"{sender} superó umbral con {count} mails")

                if bloquear_spammers and sender not in remitentes_suspendidos:
                    remitentes_suspendidos.add(sender)
                    log_prevencion("Remitente suspendido", f"{sender} bloqueado por spam")
                    enviar_alerta_mail(config, "⛔ Remitente bloqueado", f"{sender} suspendido por spam")
                else:
                    enviar_alerta_mail(config, "⚠️ Envío masivo detectado", alerta)
                break  # Solo una alerta por remitente

    return alerts