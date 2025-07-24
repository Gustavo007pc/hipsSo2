# app/detectors/cron_monitor.py

import os
import glob
import json
import re
from datetime import datetime
from app.utils.logger import log_prevencion, log_alarma
from app.utils.mailer import enviar_alerta_mail

BASELINE_FILE = '/var/log/hips/cron_baseline.json'
DEFAULT_SUSPECTS = [
    r'\bcurl\b', r'\bwget\b', r'\bnc\b',
    r'bash\s+-i', r'base64\s+-d', r'perl\s+-e',
    r'python\s+-c', r'@reboot', r'@hourly'
]

CRON_PATHS = [
    '/etc/crontab',
    '/etc/cron.d/*',
    '/var/spool/cron/crontabs/*'
]

CRON_LINE_RE = re.compile(r'''
    ^\s*
    ([\d\*\/,\-]+)\s+
    ([\d\*\/,\-]+)\s+
    ([\d\*\/,\-]+)\s+
    ([\d\*\/,\-]+)\s+
    ([\d\*\/,\-]+)\s+
    (.+)$
''', re.VERBOSE)

def load_baseline():
    if not os.path.isfile(BASELINE_FILE):
        return {}
    with open(BASELINE_FILE, 'r') as f:
        return json.load(f)

def save_baseline(baseline):
    os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)
    with open(BASELINE_FILE, 'w') as f:
        json.dump(baseline, f, indent=2)

def read_cron_file(path):
    lines = []
    try:
        with open(path, 'r') as f:
            for raw in f:
                l = raw.strip()
                if not l or l.startswith('#'):
                    continue
                if CRON_LINE_RE.match(l) or l.startswith('@'):
                    lines.append(l)
    except Exception:
        pass
    return lines

def gather_current_jobs():
    jobs = {}
    for pattern in CRON_PATHS:
        for path in glob.glob(pattern):
            jobs[path] = read_cron_file(path)
    return jobs

def is_suspicious(line, keywords):
    for kw in keywords:
        if re.search(kw, line):
            return True
    return False

def check_cron_jobs(config):
    alerts = []
    baseline = load_baseline()
    current  = gather_current_jobs()
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    settings = config.get("settings", {})
    auto_remove = settings.get("AUTO_REMOVE_CRON", False)
    keywords = settings.get("SUSPICIOUS_CRON_KEYWORDS", DEFAULT_SUSPECTS)

    for path, lines in current.items():
        old     = baseline.get(path, [])
        added   = [l for l in lines if l not in old]
        removed = [l for l in old   if l not in lines]

        for l in added:
            msg = f"{timestamp} :: Nueva entrada en {path}: “{l}”"
            alerts.append(msg)
            log_prevencion("Cron – nueva entrada", msg)

            if is_suspicious(l, keywords):
                susp = f"{timestamp} :: Comando sospechoso en {path}: “{l}”"
                alerts.append(susp)
                log_prevencion("Cron – entrada sospechosa", susp)
                enviar_alerta_mail(config, "⚠️ Cron sospechosa detectada", susp)
                try:
                    os.makedirs("logs", exist_ok=True)
                    with open("logs/cron_sospechosas.log", "a") as f:
                        f.write(f"{susp}\n")
                except:
                    pass

        for l in removed:
            msg = f"{timestamp} :: Entrada eliminada de {path}: “{l}”"
            alerts.append(msg)
            log_prevencion("Cron – entrada eliminada", msg)

        if auto_remove:
            safe = [l for l in lines if not is_suspicious(l, keywords)]
            if len(safe) < len(lines):
                try:
                    with open(path, 'w') as f:
                        f.write("\n".join(safe) + "\n")
                    msg = f"{timestamp} :: Limpieza automática aplicada en {path}"
                    alerts.append(msg)
                    log_prevencion("Cron – limpieza", msg)
                except Exception as e:
                    err = f"{timestamp} :: Error al reescribir {path}: {e}"
                    alerts.append(err)
                    log_alarma("Cron – error escritura", err)

    save_baseline(current)
    return alerts