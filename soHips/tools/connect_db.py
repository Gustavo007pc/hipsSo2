
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def con_db():
    # Conexión a la base de datos PostgreSQL
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='hips',
            user=os.getenv('bd_user'),
            password=os.getenv('bd_password')
        )
        print("Conexión a la base de datos exitosa.")
        return conn  # Retorna la conexion si es exitosa
    except Exception as e:
        print("Error al conectarse a la base de datos:", e)
        return None  # Retorna nada si hay error