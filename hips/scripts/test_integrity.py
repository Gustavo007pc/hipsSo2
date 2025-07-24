
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hashlib import sha256
from app.utils.db_connect import conectar_db
from app.utils.db_integrity import verificar_integridad



# Config falsa para registrar alertas en consola
config = {
    "log": {
        "LOG_DIR": "/tmp/",
        "PREVENCION_FILE": "test_prevencion.log"
    },
    "prevention": {
        "AUTOKILL_PROCESSES": False
    }
}

def calcular_hash(path):
    with open(path, "rb") as f:
        return sha256(f.read()).hexdigest()

def preparar_archivo_test():
    ruta = "/tmp/archivo_test_integridad.txt"
    with open(ruta, "w") as f:
        f.write("Contenido original")

    hash_original = calcular_hash(ruta)

    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO integrity_watchlist (path, sha256, last_checked, flagged) VALUES (%s, %s, NOW(), FALSE)", 
                (ruta, hash_original))
    conn.commit()
    cur.close()
    conn.close()

    return ruta

def modificar_archivo(ruta):
    with open(ruta, "w") as f:
        f.write("Contenido modificado")

def correr_prueba():
    ruta = preparar_archivo_test()
    print(f"[✔] Archivo creado y registrado: {ruta}")

    modificar_archivo(ruta)
    print(f"[⚠] Archivo modificado para disparar el detector")

    violaciones = verificar_integridad(config)
    if violaciones:
        print("[✅] Cambios detectados correctamente:")
        for v in violaciones:
            print(" →", v)
    else:
        print("[❌] El sistema NO detectó la alteración")

if __name__ == "__main__":
    correr_prueba()