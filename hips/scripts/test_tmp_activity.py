# scripts/test_tmp_activity.py
import os
import subprocess
import time

TMP_PATH = "/tmp/miner.sh"

def crear_script_malicioso():
    with open(TMP_PATH, "w") as f:
        f.write("#!/bin/bash\nwhile true; do echo 'minando...'; sleep 5; done")
    os.chmod(TMP_PATH, 0o755)
    print(f"✅ Script sospechoso creado en: {TMP_PATH}")

def ejecutar_script():
    subprocess.Popen([TMP_PATH])
    print("⚠️ Script ejecutado en segundo plano desde /tmp")

def limpiar():
    subprocess.call(["pkill", "-f", TMP_PATH])
    if os.path.exists(TMP_PATH):
        os.remove(TMP_PATH)
        print("🧼 Archivo eliminado manualmente.")
    else:
        print("✅ Archivo ya fue eliminado por el HIPS.")

if __name__ == "__main__":
    crear_script_malicioso()
    time.sleep(1)
    ejecutar_script()
    print("\n👉 Ejecutá tu HIPS ahora para verificar si detecta la actividad en /tmp.")
    input("\nPresioná Enter cuando desees limpiar el entorno...")
    limpiar()