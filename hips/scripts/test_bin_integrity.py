# scripts/test_bin_integrity.py
import time
import shutil

FILE_TO_MODIFY = "/etc/passwd"
BACKUP_FILE = "/tmp/passwd.bak"

def backup_original():
    shutil.copy2(FILE_TO_MODIFY, BACKUP_FILE)
    print("✅ Backup creado de /etc/passwd en /tmp/passwd.bak")

def modificar_archivo():
    with open(FILE_TO_MODIFY, "a") as f:
        f.write("intruso:x:1337:1337::/home/intruso:/bin/bash\n")
    print("⚠️ Entrada maliciosa agregada a /etc/passwd")

def restaurar_original():
    shutil.copy2(BACKUP_FILE, FILE_TO_MODIFY)
    print("🧼 Archivo restaurado a su versión original.")

if __name__ == "__main__":
    backup_original()
    time.sleep(1)  # breve pausa para simular evento temporal
    modificar_archivo()
    print("👉 Ejecutá ahora tu HIPS para verificar si se detecta la modificación.")
    input("\nPresioná Enter para restaurar el archivo...")
    restaurar_original()