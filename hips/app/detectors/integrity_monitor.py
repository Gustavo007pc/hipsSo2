import os
import hashlib
import json
from datetime import datetime
from app.utils.logger import log_alarma  # <--- Asegurate de que el import sea correcto

BASELINE_FILE = os.path.join(os.path.dirname(__file__), "hashes.json")

# Rutas críticas a verificar (podés ampliarlo)
CRITICAL_PATHS = ["/etc/passwd", "/etc/shadow", "/etc/sudoers"]

def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return None

def load_baseline():
    if not os.path.exists(BASELINE_FILE):
        return {}
    with open(BASELINE_FILE, "r") as f:
        return json.load(f)

def verificar_integridad_con_baseline():
    print("\n▶ Verificando integridad con baseline...")
    baseline = load_baseline()
    cambios = []

    for path in CRITICAL_PATHS:
        hash_actual = hash_file(path)
        hash_guardado = baseline.get(path)

        if hash_actual is None:
            log_alarma("Archivo inaccesible", f"No se pudo acceder a {path}")
            continue

        if hash_guardado != hash_actual:
            cambios.append((path, hash_guardado, hash_actual))
            log_alarma("Integridad modificada", f"Archivo alterado: {path}")

    if cambios:
        print(f"[{datetime.now()}] Cambios detectados en archivos críticos:")
        for path, old_hash, new_hash in cambios:
            print(f" - {path}\n   Anterior: {old_hash}\n   Actual:   {new_hash}")
    else:
        print(f"[{datetime.now()}] Sin cambios detectados.")
