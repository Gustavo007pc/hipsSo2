import subprocess
import re
from datetime import datetime

def check_mail_queue(threshold=10):
    """
    Analiza la cola de correos usando 'mailq'. Devuelve alerta si la cola supera el umbral.
    """
    try:
        result = subprocess.run(['mailq'], capture_output=True, text=True, timeout=10)
        output = result.stdout

        # Separar mails por bloques (cada mail empieza con ID hex)
        entries = []
        lines = output.splitlines()
        current_entry = []

        for line in lines:
            if re.match(r"^[A-F0-9]{5,}", line.strip(), re.IGNORECASE):
                if current_entry:
                    entries.append(current_entry)
                    current_entry = []
            current_entry.append(line)

        if current_entry:
            entries.append(current_entry)

        queue_size = len(entries)
        usuarios = set()
        oldest = None

        for entry in entries:
            for line in entry:
                # Buscar remitente tipo <user@dominio>
                match = re.search(r'<(.+?)@.+?>', line)
                if match:
                    usuarios.add(match.group(1))

                # Buscar fecha tipo "Wed Jul 24"
                date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', line)
                if date_match and not oldest:
                    oldest = line.strip()

        resumen = f"✉️ Cola actual: {queue_size} mails retenidos\n"
        resumen += f"🧑 Usuarios en cola: {', '.join(sorted(usuarios)) if usuarios else 'No identificados'}\n"
        if oldest:
            resumen += f"⏱ Mensaje más antiguo: {oldest}\n"

        if queue_size > threshold:
            resumen += f"🚨 Alerta: cola supera umbral ({threshold})"

        return resumen

    except Exception as e:
        return f"❌ Error al verificar cola de mails: {e}"