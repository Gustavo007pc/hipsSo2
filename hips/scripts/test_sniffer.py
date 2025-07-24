import os
import subprocess

def activar_modo_promiscuo():
    subprocess.run(["ip", "link", "set", "eth0", "promisc", "on"], check=True)
    print("Modo promiscuo activado.")

def iniciar_tcpdump():
    subprocess.Popen(["tcpdump", "-i", "eth0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("tcpdump iniciado en segundo plano.")

def ejecutar_simulacion():
    try:
        activar_modo_promiscuo()
        iniciar_tcpdump()
    except Exception as e:
        print(f"Error en la simulación: {e}")

if __name__ == "__main__":
    ejecutar_simulacion()