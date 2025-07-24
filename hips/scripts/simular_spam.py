import subprocess
import time

REMITENTE = "hips@localhost"
DESTINO = "admin@localhost"
MENSAJE = "Esto es un correo simulado del sistema HIPS para testeo de spam."
ASUNTO  = "Spam de prueba 🚨"

def enviar_mail():
    try:
        subprocess.run([
            "sendmail", DESTINO
        ], input=f"Subject: {ASUNTO}\nFrom: {REMITENTE}\n\n{MENSAJE}\n", text=True)
    except Exception as e:
        print(f"[ERROR] Fallo envío: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando simulación de envío masivo...")
    for i in range(20):  # cantidad para superar el umbral
        enviar_mail()
        time.sleep(1)  # ajustá si querés acelerar o espaciar
    print("✅ Simulación completa. Revisá /mails para ver si se detectó.")