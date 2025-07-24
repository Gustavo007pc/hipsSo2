import json
import time
import datetime
import sys

from app.detectors import (
    bin_integrity,
    logged_users,
    sniffers,
    log_analyzer,
    mail_queue,
    mail_monitor,
    integrity_monitor,
    ddos_detector,
    process_monitor,
    memory_monitor,
    tmp_monitor,
    cron_monitor
)

from app.utils import process_killer
from app.utils.logger import log_prevencion
from app.utils.mailer import enviar_alerta_mail

CONFIG_PATH = "config.json"

# Configuración por defecto
DEFAULT_CONFIG = {
    "modules": {
        "memory_monitor": True,
        "cron_monitor": True,
        "ddos_detector": True,
        "process_monitor": True
    },
    "settings": {
        "CONN_THRESHOLD": 200,
        "MAX_REQUESTS": 100,
        "TIME_WINDOW": 60,
        "ENABLE_MAIL": False,
        "ADMIN_EMAIL": "admin@example.com",
        "SMTP_SERVER": "smtp.example.com",
        "SMTP_PORT": 587,
        "EMAIL_USER": "hips@example.com",
        "EMAIL_PASS": "password_segura",
        "TEST_MODE": False,
        "LOG_LINES": 1000
    },
    "whitelist": ["Xorg", "systemd", "sshd", "bash", "code"]
}

def get_live_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] No se pudo cargar config.json: {e}")
        return DEFAULT_CONFIG

def registrar_ejecucion():
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open("/var/log/hips/ejecucion.log", "a") as f:
            f.write(ts + "\n")
    except:
        print("[WARN] No se pudo registrar la ejecución")

def activar_modulo(nombre, config):
    return config.get("modules", {}).get(nombre, False)

def ejecutar_detectores(config):
    registrar_ejecucion()

    settings = config.get("settings", {})
    whitelist = config.get("whitelist", [])
    test_mode = settings.get("TEST_MODE", False)
    suspicious_pids = []
    resumen_alertas = {}

    def registrar_alertas(modulo, alertas):
        resumen_alertas[modulo] = len(alertas)
        if not alertas:
            print(f"No se detectaron eventos en {modulo}.")
        for alert in alertas:
            print(alert)
            enviar_alerta_mail(config, f"⚠️ Alerta en {modulo}", alert)

    print("▶ Verificando integridad de archivos críticos...")
    registrar_alertas("bin_integrity", bin_integrity.check_system_files())

    print("\n▶ Verificando usuarios UID 0 conectados...")
    registrar_alertas("logged_users", logged_users.detect_uid0_processes())

    print("\n▶ Verificando sniffers activos...")
    registrar_alertas("sniffers", sniffers.check_sniffers())

    print("\n▶ Analizando logs de autenticación...")
    registrar_alertas("log_analyzer", log_analyzer.analyze_auth_logs(config))

    print("\n▶ Verificando cola de mails...")
    cola_alerta = mail_queue.check_mail_queue()
    if cola_alerta:
        print(cola_alerta)
        enviar_alerta_mail(config, "⚠️ Cola de mails sospechosa", cola_alerta)

    print("\n▶ Verificando envíos masivos de mails...")
    registrar_alertas("mail_monitor", mail_monitor.detect_mass_mailing(config))

    print("\n▶ Verificando integridad con baseline...")
    integrity_monitor.verificar_integridad_con_baseline()

    if activar_modulo("ddos_detector", config):
        print("\n▶ Detectando ataques DDOS en DNS…")
        registrar_alertas("ddos_detector", ddos_detector.detect_ddos(config))

    if activar_modulo("memory_monitor", config):
        print("\n▶ Monitoreando procesos con alto consumo de memoria...")
        mem_alerts = memory_monitor.check_memory_usage()
        resumen_alertas["memory_monitor"] = len(mem_alerts)
        for alert in mem_alerts:
            print(alert)
            log_prevencion("Memoria alta", alert)
            enviar_alerta_mail(config, "⚠️ Memoria excesiva", alert)

    if activar_modulo("process_monitor", config):
        print("\n▶ Verificando procesos sospechosos...")
        alerts, suspicious_pids = process_monitor.check_suspicious_processes(whitelist)
        resumen_alertas["process_monitor"] = len(alerts)
        for alert in alerts:
            print(alert)
            enviar_alerta_mail(config, "⚠️ Proceso sospechoso", alert)

    print("\n▶ Verificando actividad sospechosa en /tmp...")
    try:
        tmp_alerts = tmp_monitor.eliminar_tmp_procesos_y_archivos(config)
        registrar_alertas("tmp_monitor", tmp_alerts)
    except Exception as e:
        print(f"[ERROR] /tmp monitor falló: {e}")

    if activar_modulo("cron_monitor", config):
        print("\n▶ Verificando tareas programadas en cron...")
        cron_alerts = cron_monitor.check_cron_jobs(config)
        registrar_alertas("cron_monitor", cron_alerts)

    # Resumen final
    ts = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open("logs/resumen_ejecucion.log", "a") as f:
        f.write(f"{ts} :: Ejecución completa\n")
        for modulo, cantidad in resumen_alertas.items():
            f.write(f"{ts} :: {modulo} → {cantidad} alertas\n")

    # Acción manual
    if suspicious_pids and not test_mode:
        while True:
            respuesta = input("\n¿Eliminar procesos sospechosos detectados? (s/n): ").lower()
            if respuesta in ["s", "n"]:
                break
            print("Entrada inválida. Usa 's' o 'n'.")
        if respuesta == "s":
            for pid in suspicious_pids:
                if process_killer.kill_process(pid):
                    mensaje = f"Proceso PID {pid} eliminado manualmente"
                    print(mensaje)
                    log_prevencion("Proceso eliminado", mensaje)
                    enviar_alerta_mail(config, "✅ Proceso eliminado", mensaje)
                    with open("logs/manual_actions.log", "a") as f:
                        f.write(f"{ts} :: {mensaje}\n")
                else:
                    print(f"No se pudo eliminar el proceso PID {pid}.")

def main_loop():
    while True:
        config = get_live_config()
        print("\n🧠 Configuración cargada. Ejecutando análisis...")
        ejecutar_detectores(config)
        print("\n⏳ Esperando 60 segundos para el próximo ciclo...\n")
        time.sleep(60)

if __name__ == "__main__":
    if "once" in sys.argv:
        config = get_live_config()
        ejecutar_detectores(config)
    else:
        main_loop()