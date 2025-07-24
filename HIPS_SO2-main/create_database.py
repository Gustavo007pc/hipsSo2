import subprocess
import os
import psycopg2
PASSWD_DIR = "/etc/passwd"
SHADOW_DIR = "/etc/shadow"

import os
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

# Archivos a verificar
PASSWD_DIR = "/etc/passwd"
SHADOW_DIR = "/etc/shadow"


def create_database():
    conn=con_db()
    cursor=conn.cursor()
    # Crear la tabla 'file_hashes' en la base de datos si no existe y los hashes para /etc/passwd y shadow iniciales
    hash_passwd_init = subprocess.run(["sudo", "sha256sum", PASSWD_DIR], check=True, capture_output=True).stdout.decode().strip().split()[0]
    hash_shadow_init = subprocess.run(["sudo", "sha256sum", SHADOW_DIR], check=True, capture_output=True).stdout.decode().strip().split()[0] 
    cursor.execute('DROP TABLE IF EXISTS file_hashes;')
    cursor.execute(
        """
        CREATE TABLE file_hashes (
            id SERIAL PRIMARY KEY,
            file_path TEXT NOT NULL,
            file_hash TEXT NOT NULL
        );
        """
    )
    cursor.execute("INSERT INTO file_hashes(file_path, file_hash) VALUES (%s,%s), (%s,%s);",(PASSWD_DIR, hash_passwd_init, SHADOW_DIR, hash_shadow_init))

    conn.commit()
    #Crear la tabla donde se guarda el usuarios
    cursor.execute('DROP TABLE IF EXISTS users;')
    cursor.execute(
        """

        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL

        );  """
    )
    #Insertar las credenciales de admin
    cursor.execute("INSERT INTO users (username, password, email) VALUES('admin', '12345', 'christian55501@gmail.com');")
    conn.commit()
    cursor.close()
    conn.close()

create_database()