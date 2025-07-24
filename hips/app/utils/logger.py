import os
from datetime import datetime
import smtplib
from email.message import EmailMessage
ENABLE_MAIL = False   # ← cambiar a True solo en producción
# Rutas de archivos de log para alertas y acciones de prevención
ALERT_LOG = "/var/log/hips/alertas.log"
PREV_LOG = "/var/log/hips/prevencion.log"

# Email del administrador para recibir notificaciones
ADMIN_EMAIL = "admin@example.com"  # <-- Reemplazá esto por tu correo real

# Asegurar que el directorio de logs exista
os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
os.makedirs(os.path.dirname(PREV_LOG), exist_ok=True)

def write_log(file_path, message):
    """
    Escribe un mensaje con timestamp en el archivo de log especificado.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        with open(file_path, "a") as f:
            f.write(f"{timestamp} :: {message}\n")
    except Exception as e:
        print(f"Error escribiendo en log {file_path}: {e}")

def send_email(subject, body):
    """
    Envía un correo con el asunto y cuerpo indicados al ADMIN_EMAIL.
    Solo si ENABLE_MAIL está en True.
    """
    if not ENABLE_MAIL:
        # En modo test, simplemente registrar local
        color = "\033[93m" if "Alarma" in subject else "\033[92m"
        print(f"📨 Email (simulado): [{subject}] {body}")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = "hips@localhost"
    msg["To"] = ADMIN_EMAIL

    try:
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Error enviando email: {e}")

    try:
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Error enviando email: {e}")

def log_alarma(tipo, mensaje, ip_origen=None):
    """
    Loguea una alerta detectada en ALERT_LOG y envía mail al admin.
    ip_origen es opcional para agregar IP si está disponible.
    """
    ip_text = f" :: IP: {ip_origen}" if ip_origen else ""
    log_msg = f"{tipo}{ip_text} :: {mensaje}"
    write_log(ALERT_LOG, log_msg)
    send_email(f"Alarma HIPS: {tipo}", mensaje)

def log_prevencion(mensaje, ip_origen=None):
    """
    Loguea una acción de prevención tomada en PREV_LOG y envía mail al admin.
    ip_origen es opcional para agregar IP si está disponible.
    """
    ip_text = f" :: IP: {ip_origen}" if ip_origen else ""
    log_msg = f"Prevención{ip_text} :: {mensaje}"
    write_log(PREV_LOG, log_msg)
    send_email("Acción de prevención HIPS", mensaje)

def log_alert(*args):
    """
    Compatibilidad flexible:
    - log_alert("Mensaje") → tipo = 'Alerta'
    - log_alert("Tipo personalizado", "Mensaje")
    """
    if len(args) == 1:
        log_alarma("Alerta", args[0])
    elif len(args) == 2:
        log_alarma(args[0], args[1])
    else:
        raise ValueError("log_alert espera 1 o 2 argumentos.")
