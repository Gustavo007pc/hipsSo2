import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.mailer import enviar_alerta_mail
import json

def cargar_config():
    try:
        with open("../config.json") as f:
            return json.load(f)
    except:
        print("⚠️ No se pudo leer config.json")
        return {
            "settings": {
                "ENABLE_MAIL": False,
                "EMAIL_USER": "prueba@example.com",
                "EMAIL_PASS": "clave_fake",
                "ADMIN_EMAIL": "admin@example.com",
                "SMTP_SERVER": "smtp.fake.com",
                "SMTP_PORT": 587
            }
        }

if __name__ == "__main__":
    config = cargar_config()

    asunto = "🧪 Prueba de envío HIPS"
    cuerpo = "Este es un mensaje de prueba del sistema HIPS para verificar el envío de alertas por correo.\n\nSi estás viendo esto, el canal SMTP está funcionando correctamente ✅."

    enviar_alerta_mail(config, asunto, cuerpo)
    print("📤 Intento de envío realizado. Revisá tu bandeja o log.")