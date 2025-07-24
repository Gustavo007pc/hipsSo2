import os
import subprocess
import psutil
import shutil
import hashlib
from datetime import datetime
from app.utils.logger import log_alarma, log_prevencion
from app.utils.mailer import enviar_alerta_mail

SUSPICIOUS_KEYWORDS = ["miner", "shell", "bot", "mal", "rat", "backdoor", "payload", "rev"]
TMP_DIR = "/tmp"
QUARANTINE_DIR = "/var/hips/tmp_quarantine"

def es_binario_ejecutable(path):
    try:
        result = subprocess.run(["file", path], capture_output=True, text=True)
        info = result.stdout.lower()
        return "elf" in info or "script" in info or "executable" in info
    except Exception:
        return False

def sha256sum(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return "error"

def eliminar_tmp_procesos_y_archivos(config=None):
    alerts = []
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    cuarentena_activa = config.get("prevention", {}).get("QUARANTINE_TMP", False)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)

    # 1. Procesos desde /tmp
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            pid = proc.info['pid']
            cmd = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
            exe = proc.info['exe'] or ""

            if "/tmp/" in cmd or "/tmp/" in exe:
                if any(k in cmd.lower() for k in SUSPICIOUS_KEYWORDS):
                    alerta = f"{timestamp} :: Proceso sospechoso desde /tmp: {cmd} (PID {pid})"
                    alerts.append(alerta)
                    log_alarma("Proceso sospechoso en /tmp", alerta)
                    log_prevencion("Proceso terminado", f"{cmd} (PID {pid}) eliminado")
                    enviar_alerta_mail(config, "⚠️ Proceso en /tmp", alerta)
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 2. Archivos en /tmp
    for root, dirs, files in os.walk(TMP_DIR):
        for fname in files:
            path = os.path.join(root, fname)
            try:
                if any(k in fname.lower() for k in SUSPICIOUS_KEYWORDS) or es_binario_ejecutable(path):
                    sha = sha256sum(path)

                    if cuarentena_activa:
                        destino = os.path.join(QUARANTINE_DIR, fname)
                        shutil.copy(path, destino)

                    os.chmod(path, 0o644)
                    os.remove(path)

                    alerta = f"{timestamp} :: Archivo sospechoso eliminado: {path} (SHA256: {sha})"
                    alerts.append(alerta)
                    log_alarma("Archivo eliminado en /tmp", alerta)
                    log_prevencion("Archivo cuarentenado", alerta)
                    enviar_alerta_mail(config, "⚠️ Archivo malicioso en /tmp", alerta)
            except Exception as e:
                log_alarma("Error analizando /tmp", f"{path} → {e}")

    return alerts