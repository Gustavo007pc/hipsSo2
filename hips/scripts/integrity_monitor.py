
import json

with open("config.json") as f:
    config = json.load(f)

from app.utils.db_integrity import verificar_integridad

violaciones = verificar_integridad(config)
for v in violaciones:
    print(v)