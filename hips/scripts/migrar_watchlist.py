import os
import psycopg2
from dotenv import load_dotenv
from hashlib import sha256

load_dotenv()

def conectar_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432)
    )

def calcular_sha256(path):
    try:
        with open(path, "rb") as f:
            return sha256(f.read()).hexdigest()
    except:
        return None  # archivo inaccesible o no encontrado

def migrar_txt_a_postgres(txt_path="integrity_watchlist.txt"):
    if not os.path.exists(txt_path):
        print(f"[ERROR] No existe el archivo {txt_path}")
        return

    with open(txt_path) as f:
        rutas = [line.strip() for line in f if line.strip()]

    conn = conectar_db()
    cur = conn.cursor()
    insertados = 0

    for ruta in rutas:
        hash_calculado = calcular_sha256(ruta)
        if hash_calculado:
            cur.execute(
                "INSERT INTO integrity_watchlist (path, sha256, last_checked, flagged) VALUES (%s, %s, NOW(), FALSE)",
                (ruta, hash_calculado)
            )
            insertados += 1
        else:
            print(f"[WARN] No se pudo acceder a: {ruta}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Migración completa: {insertados} rutas insertadas")

if __name__ == "__main__":
    migrar_txt_a_postgres()