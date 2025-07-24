import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.db_connect import conectar_db



conn = conectar_db()
if conn:
    print("✅ Conexión exitosa")
    conn.close()
else:
    print("❌ Falló la conexión")