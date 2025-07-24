import os
import signal

def kill_process(pid):
    protected_pids = {os.getpid(), os.getppid()}  # El script actual y su padre (ej. terminal)

    if pid in protected_pids:
        # No imprimir aquí, solo retornar False para que run.py maneje el mensaje
        return False

    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except PermissionError:
        return False
    except ProcessLookupError:
        return False
    except Exception:
        return False
