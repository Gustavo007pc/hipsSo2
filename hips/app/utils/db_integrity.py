import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from hashlib import sha256
from app.utils.db_connect import conectar_db
from app.utils.registrar_prevencion import registrar_prevencion

load_dotenv()

def calcular_hash(path):
    try:
        with open(path, "rb") as f:
            return sha256(f.read()).hexdigest()
    except Exception as e:
        return f"error:{e}"

def obtener_watchlist():
    conn = conectar_db()
    if not conn:
        return []

    cur = conn.cursor()
    cur.execute("SELECT id, path, sha256 FROM integrity_watchlist WHERE flagged = FALSE;")
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado

def verificar_integridad(config=None):
    alterados = []

    for id_archivo, ruta, hash_guardado in obtener_watchlist():
        hash_actual = calcular_hash(ruta)
        if hash_actual != hash_guardado:
            alerta = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} :: Alteración detectada en {ruta}"
            alterados.append(alerta)

            conn = conectar_db()
            cur = conn.cursor()
            cur.execute("UPDATE integrity_watchlist SET flagged = TRUE, last_checked = %s WHERE id = %s;",
                        (datetime.now(), id_archivo))
            conn.commit()
            cur.close()
            conn.close()

            registrar_prevencion(config, f"Integridad comprometida: {ruta}", origen="localhost", modulo="integrity_monitor")

    return alterados