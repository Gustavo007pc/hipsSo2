from app.utils.logger import log_alarma, log_prevencion

log_alarma("Intento de modificación de /etc/shadow", "192.168.1.23")
log_prevencion("Proceso sospechoso terminado", "192.168.1.23")

print("Logs escritos correctamente.")
