import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432)
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Conexión fallida: {e}")
        return None