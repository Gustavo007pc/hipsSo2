import os
import psutil
import subprocess

SNIFFERS = ["tcpdump", "wireshark", "tshark", "ettercap", "dsniff"]

def is_promiscuous(interface):
    try:
        with open(f"/sys/class/net/{interface}/flags", "r") as f:
            flags = int(f.read().strip(), 16)
            return bool(flags & 0x100)  # IFF_PROMISC
    except:
        return False

def disable_promiscuous(interface):
    subprocess.call(["ip", "link", "set", interface, "promisc", "off"])

def kill_sniffers():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in SNIFFERS:
            print(f"[!] Terminando proceso sospechoso: {proc.info['name']} (PID: {proc.info['pid']})")
            try:
                psutil.Process(proc.info['pid']).kill()
            except Exception as e:
                print(f"    Error al eliminar proceso: {e}")

def run():
    print("[*] Verificando interfaces en modo promiscuo...")
    interfaces = os.listdir('/sys/class/net/')
    for iface in interfaces:
        if is_promiscuous(iface):
            print(f"[!] {iface} está en modo promiscuo. Desactivando...")
            disable_promiscuous(iface)

    print("[*] Buscando herramientas de sniffing en ejecución...")
    kill_sniffers()

if __name__ == "__main__":
    run()
