import smtplib
import ssl
from email.message import EmailMessage
import os
import datetime

def enviar_alerta_mail(config, asunto, mensaje):
    modo = config.get("settings", {}).get("EMAIL_MODE", "real")
    habilitado = config.get("settings", {}).get("ENABLE_MAIL", False)

    if not habilitado:
        return

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if modo == "local":
        simulado = f"[{timestamp}] Simulación de envío:\nAsunto: {asunto}\nContenido:\n{mensaje}\n\n"
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/mails_simulados.log", "a") as f:
                f.write(simulado)
            print(f"📨 Email (simulado): [{asunto}] {mensaje.splitlines()[0]}")
        except Exception as e:
            print(f"[ERROR] Simulación de envío falló: {e}")
        return

    # Modo real: SMTP
    try:
        msg = EmailMessage()
        msg.set_content(mensaje)
        msg["Subject"] = asunto
        msg["From"] = config["settings"]["EMAIL_USER"]
        msg["To"] = config["settings"]["ADMIN_EMAIL"]

        context = ssl.create_default_context()
        with smtplib.SMTP(config["settings"]["SMTP_SERVER"], config["settings"]["SMTP_PORT"]) as server:
            server.starttls(context=context)
            server.login(config["settings"]["EMAIL_USER"], config["settings"]["EMAIL_PASS"])
            server.send_message(msg)

        print(f"📧 Alerta enviada por correo a {msg['To']}")
    except Exception as e:
        print(f"[ERROR] Fallo al enviar correo: {e}")