import hashlib
import os
import json
from datetime import datetime
from app.utils.logger import log_alarma  # Logger unificado

HASH_STORE = "app/detectors/hashes.json"

def calculate_sha256(path):
    """Calcula el hash SHA256 del archivo dado."""
    try:
        with open(path, "rb") as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    except FileNotFoundError:
        log_alarma("Integridad binaria", f"Archivo no encontrado: {path}", ip_origen="localhost")
    except PermissionError:
        log_alarma("Integridad binaria", f"Permiso denegado leyendo archivo: {path}", ip_origen="localhost")
    except Exception as e:
        log_alarma("Integridad binaria", f"Error leyendo archivo {path}: {e}", ip_origen="localhost")
    return None

def load_known_hashes():
    """Carga hashes conocidos desde archivo JSON."""
    if not os.path.exists(HASH_STORE):
        return {}
    with open(HASH_STORE, "r") as f:
        return json.load(f)

def save_known_hashes(hashes):
    """Guarda hashes actuales en archivo JSON."""
    with open(HASH_STORE, "w") as f:
        json.dump(hashes, f, indent=2)

def check_system_files():
    """
    Verifica integridad de archivos críticos.
    Retorna lista de alertas detectadas.
    """
    files = ["/etc/passwd", "/etc/shadow"]
    known_hashes = load_known_hashes()
    current_alerts = []

    for path in files:
        current_hash = calculate_sha256(path)
        if current_hash is None:
            # Ya se logueó el error en calculate_sha256, solo seguir
            continue

        known_hash = known_hashes.get(path)

        if known_hash is None:
            # Primera vez que se verifica, guardamos el hash
            known_hashes[path] = current_hash
        elif known_hash != current_hash:
            alert = f"Modificación detectada en {path} :: localhost"
            current_alerts.append(alert)
            log_alarma("Integridad binaria", alert, ip_origen="localhost")
            known_hashes[path] = current_hash  # Actualizamos para la próxima vez

    save_known_hashes(known_hashes)
    return current_alerts
