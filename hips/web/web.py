from flask import Flask, render_template, redirect, url_for, request, session
import os
import json
import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Cambiar en producción

# Credenciales de acceso
USERNAME = "admin"
PASSWORD = "hipspassword"

# Rutas de log
ALERT_LOG = "/var/log/hips/alertas.log"
PREV_LOG = "/var/log/hips/prevencion.log"
CONFIG_PATH = "config.json"

# Configuración por defecto
default_config = {
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
        "ENABLE_MAIL": False
    },
    "whitelist": ["Xorg", "systemd", "sshd", "bash", "code"]
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u == USERNAME and p == PASSWORD:
            session["user"] = u
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if not os.path.isfile(ALERT_LOG):
        alerts = ["No hay alertas registradas."]
    else:
        with open(ALERT_LOG) as f:
            alerts = f.readlines()[-40:]
    return render_template("dashboard.html", alerts=alerts)

@app.route("/prevencion")
def prevencion():
    if "user" not in session:
        return redirect(url_for("login"))

    if not os.path.isfile(PREV_LOG):
        eventos = ["No hay registros de prevención."]
    else:
        with open(PREV_LOG) as f:
            eventos = f.readlines()[-50:]
    return render_template("prevencion.html", eventos=eventos)

@app.route("/configuracion", methods=["GET", "POST"])
def configuracion():
    if "user" not in session:
        return redirect(url_for("login"))

    import json
    from flask import request, render_template

    config_path = "../config.json"

    try:
        with open(config_path) as f:
            config = json.load(f)
    except:
        config = {}

    # Agregar módulos faltantes
    todos_los_modulos = [
        "memory_monitor", "cron_monitor", "ddos_detector", "process_monitor",
        "sniffers", "bin_integrity", "logged_users", "integrity_monitor"
    ]
    for mod in todos_los_modulos:
        config.setdefault("modules", {}).setdefault(mod, False)

    mensaje = ""
    success = False

    if request.method == "POST":
        try:
            # Módulos
            for mod in config["modules"]:
                campo = f"modules_{mod}"
                config["modules"][mod] = campo in request.form

            # Settings
            for clave in config["settings"]:
                campo = f"settings_{clave}"
                actual = config["settings"][clave]
                if isinstance(actual, bool):
                    config["settings"][clave] = campo in request.form
                elif isinstance(actual, int):
                    valor = request.form.get(campo, "").strip()
                    if valor.isdigit():
                        config["settings"][clave] = int(valor)
                else:
                    config["settings"][clave] = request.form.get(campo, actual)

            # Whitelist
            texto_whitelist = request.form.get("whitelist", "")
            procesos = [p.strip() for p in texto_whitelist.split(",") if p.strip()]
            config["whitelist"] = procesos

            # Guardar
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            mensaje = "✅ Configuración actualizada correctamente."
            success = True
        except Exception as e:
            mensaje = f"❌ Error al guardar configuración: {e}"
            success = False

    return render_template("configuracion.html", config=config, mensaje=mensaje, success=success)
@app.route("/mails")
def mails():
    if "user" not in session:
        return redirect(url_for("login"))

    import datetime
    import json
    from app.detectors import mail_queue, mail_monitor

    with open("config.json") as f:
        config = json.load(f)

    cola = mail_queue.check_mail_queue(threshold=config["settings"].get("MAX_MAILS", 10))
    spam_alerts = mail_monitor.detect_mass_mailing(config)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("mails.html", cola=cola, spam_alerts=spam_alerts, timestamp=timestamp)

@app.route("/exportar_mails")
def exportar_mails():
    from flask import Response
    import datetime
    from app.detectors import mail_queue, mail_monitor

    cola = mail_queue.check_mail_queue(threshold=10)
    spam_alerts = mail_monitor.detect_mass_mailing()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    contenido = [
        f"🕒 Reporte de mails generado: {timestamp}\n",
        f"✉️ Cola de correos:\n{cola or 'Sin datos'}\n",
        "🚨 Eventos de mailing masivo:\n"
    ]
    contenido += [f" - {a}" for a in spam_alerts] if spam_alerts else [" - Ninguno detectado"]

    return Response("\n".join(contenido), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=hips_mails.txt"})


@app.route("/cron")
def cron():
    if "user" not in session:
        return redirect(url_for("login"))

    from app.detectors import cron_monitor
    import json

    with open("config.json") as f:
        config = json.load(f)

    eventos = cron_monitor.check_cron_jobs(config)
    return render_template("cron.html", eventos=eventos)

@app.route("/cron/exportar")
def cron_exportar():
    from flask import Response
    from app.detectors import cron_monitor
    import json

    with open("config.json") as f:
        config = json.load(f)

    eventos = cron_monitor.check_cron_jobs(config)
    contenido = "\n".join(eventos) if eventos else "Sin cambios detectados en cron."
    return Response(contenido, mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=cron_resumen.txt"})


@app.route("/estado")
def estado():
    if "user" not in session:
        return redirect(url_for("login"))

    # Cargar config
    config_path = "config.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
    except:
        config = default_config

    # Leer logs
    alert_count = {}
    prevencion_count = {}

    try:
        with open("/var/log/hips/alertas.log") as f:
            for line in f:
                tipo = line.split("::")[1].strip() if "::" in line else "Desconocido"
                alert_count[tipo] = alert_count.get(tipo, 0) + 1
    except:
        pass

    try:
        with open("/var/log/hips/prevencion.log") as f:
            for line in f:
                tipo = line.split("::")[1].strip() if "::" in line else "Desconocido"
                prevencion_count[tipo] = prevencion_count.get(tipo, 0) + 1
    except:
        pass

    # Calcular última ejecución
    try:
        with open("/var/log/hips/alertas.log") as f:
            last_line = f.readlines()[-1]
            ultima_ejecucion = last_line.split("::")[0].strip()
    except:
        ultima_ejecucion = "Sin registro"

    return render_template("estado.html",
                           config=config,
                           alert_count=alert_count,
                           prevencion_count=prevencion_count,
                           ultima_ejecucion=ultima_ejecucion)


@app.route("/exportar_resumen")
def exportar_resumen():
    from flask import Response
    try:
        with open("config.json") as f:
            config = json.load(f)
    except:
        config = default_config

    resumen = []
    resumen.append("📊 Resumen del sistema HIPS\n")
    resumen.append(f"🕒 Última ejecución: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    resumen.append("✅ Módulos activos:\n")
    for k,v in config.get("modules", {}).items():
        resumen.append(f" - {k}: {'activo' if v else 'inactivo'}\n")

    resumen.append("\n📈 Alertas:\n")
    try:
        with open("/var/log/hips/alertas.log") as f:
            for line in f:
                tipo = line.split("::")[1].strip() if "::" in line else "Desconocido"
                resumen.append(f" - {tipo}\n")
    except:
        resumen.append(" - No se encontraron alertas\n")

    resumen.append("\n🛡️ Prevención:\n")
    try:
        with open("/var/log/hips/prevencion.log") as f:
            for line in f:
                tipo = line.split("::")[1].strip() if "::" in line else "Desconocido"
                resumen.append(f" - {tipo}\n")
    except:
        resumen.append(" - No se encontraron acciones\n")

    return Response("\n".join(resumen), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=hips_resumen.txt"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)