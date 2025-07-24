import os
from datetime import datetime
from app.utils.mailer import enviar_alerta_mail

LOG_PATH = "/var/log/hips/prevencion.log"

def registrar_prevencion(config, accion, origen="localhost", modulo="sistema"):
    """
    Registra una acción preventiva y envía alerta al administrador.

    - accion: Descripción de la acción ejecutada
    - origen: IP o nombre de usuario (ej: '192.168.1.10' o 'root')
    - modulo: Nombre del módulo que disparó la acción (ej: 'process_monitor')
    """
    ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linea = f"{ts} :: PREVENCION :: {accion} :: {origen} :: Módulo: {modulo}\n"

    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(linea)

        asunto = f"🛡️ Acción preventiva: {modulo}"
        cuerpo = f"{linea.strip()}"
        enviar_alerta_mail(config, asunto, cuerpo)
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo registrar prevención: {e}")
        return False