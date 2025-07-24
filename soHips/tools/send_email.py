import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

# Cargar las variables de entorno
bd_password = os.getenv('bd_password')
bd_user = os.getenv('bd_user')

hips_email = os.getenv("hips_email")
hips_email_password = os.getenv("hips_email_password")

hips_email_admin = os.getenv("hips_email_admin")

def send_email_admin(alert_type, subject, body):
    try:
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = 587  # Puerto para TLS/STARTTLS

        context = ssl.create_default_context()

        with smtplib.SMTP(smtp_server, smtp_port) as connection:
            connection.starttls(context=context)  # Establecer conexión segura con TLS
            connection.login(user=hips_email, password=hips_email_password)

            message = f"Subject: {alert_type} {subject}\n\n{body}"
            connection.sendmail(from_addr=hips_email, to_addrs=hips_email_admin, msg=message)
    except Exception as e:
        print(f"Error al mandar correo: {e}")

