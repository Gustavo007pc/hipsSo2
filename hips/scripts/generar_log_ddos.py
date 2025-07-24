# scripts/generar_log_ddos.py
import time
from datetime import datetime

DNS_LOG = "/var/log/dns_attack.log"
IP_ATACANTE = "192.168.100.99"
PETICIONES = 120  # más de MAX_REQUESTS
SERVICIO = "dns"

def generar_log():
    with open(DNS_LOG, "w") as f:
        for _ in range(PETICIONES):
            timestamp = datetime.now().strftime("%b %d %H:%M:%S")
            linea = f"{timestamp} {SERVICIO}[1234]: request from {IP_ATACANTE}\n"
            f.write(linea)
            time.sleep(0.3)  # espacio entre peticiones

    print(f"✅ Log falso generado en {DNS_LOG} con {PETICIONES} peticiones desde {IP_ATACANTE}")

if __name__ == "__main__":
    generar_log()