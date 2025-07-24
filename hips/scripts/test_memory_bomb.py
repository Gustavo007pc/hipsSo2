# scripts/test_memory_bomb.py
import numpy as np
import time

class MemoryBomb:
    def __init__(self, size_mb=1000, duration_sec=600):
        self.size_mb = size_mb
        self.duration_sec = duration_sec

    def explode(self):
        print(f"💣 Iniciando consumo de {self.size_mb}MB RAM durante {self.duration_sec} segundos...")
        # Convertir MB a número de floats (~8 bytes por float)
        num_floats = int((self.size_mb * 1024 * 1024) / 8)
        data = np.ones(num_floats, dtype=np.float64)  # bloque de RAM

        start = time.time()
        while time.time() - start < self.duration_sec:
            time.sleep(1)
        print("🧼 Proceso finalizado. Liberando memoria...")

if __name__ == "__main__":
    bomb = MemoryBomb(size_mb=1000, duration_sec=600)
    bomb.explode()