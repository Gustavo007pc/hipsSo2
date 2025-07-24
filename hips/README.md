# 🛡️ HIPS: Sistema de Prevención de Intrusiones basado en Host

**Alumno:** Gustavo Perez
**Curso:** Sistema Operativo 2  
**Entrega:** Proyecto Final – HIPS funcional con detección de integridad y ataques DDoS

---

## 📌 Funciones principales del sistema

El sistema HIPS verifica de forma continua múltiples aspectos críticos del sistema:

- 🧬 Verificación de integridad de archivos sensibles (`/etc/passwd`, `/etc/shadow`, binarios del sistema)
- 👥 Control de usuarios conectados y sus orígenes
- 🕵️‍♂️ Detección de sniffers activos en el sistema
- 🧾 Análisis de logs `/var/log/messages`, `/var/log/secure`, `/var/log/maillog`, `/var/log/httpd/access_log`
- 📧 Verificación de envíos masivos en la cola de correos (`mailq`)
- 🧮 Monitoreo de consumo de CPU y memoria
- 🚨 Detección de ataques DDoS por:
  - Análisis de logs DNS
  - Detección de conexiones vivas al puerto 53
- 🐚 Archivos sospechosos en `/tmp`
- ⏱️ Verificación de tareas cron sospechosas
- ❌ Intentos de acceso indebido al sistema

---

## ⚙️ Tecnologías utilizadas

- `Python`
- `Flask`
- `PostgreSQL`
- `psycopg2`, `dotenv`, `cryptography`, `psutil`, `subprocess`
- Reglas dinámicas con `iptables`
- Alertas y prevención vía log + bloqueo

---

## 🧰 Requisitos del sistema

- `Debian / Kali Linux` *(adaptable también a CentOS con modificaciones)*
- `Python 3`, `pip`
- `PostgreSQL 17.x`
- Acceso con privilegios de administrador

---

### 1. Crear entorno virtual

python3 -m venv hips_venv
source hips_venv/bin/activate

### 2. Instalar dependencias

pip install -r requirements.txt


### 3. Instalar dependencias

pip install -r requirements.txt

### 4. Instalar dependencias

DB_NAME=hips
DB_USER=hips_writer
DB_PASS=tu_clave
HASH_SECRET=tu_clave_fernet
ENABLE_MAIL=true
HIPS_MAIL=correo@hipssystem.com
MAIL_PASS=clave_correo
ADMIN_MAIL=admin@institucion.edu


Protegé este archivo con:
chmod 600 .env



### 5. Crear carpeta de logs
sudo mkdir -p /var/log/hips/output/
sudo touch /var/log/hips/alarmas.log
sudo touch /var/log/hips/prevencion.log



### 🗄️ Inicializar la base de datos
Ingresá a psql y ejecutá el script:
psql -U postgres -d hips -f scripts/init_integrity.sql

### 🔍 Test de integridad funcional
python3 scripts/test_integrity.py


🌐 Ejecución del sistema (opcional interfaz Flask)
export FLASK_APP=app
flask run


### Abrí tu navegador en:
http://127.0.0.1:5000
Usuario: admin
Contraseña: hipspassword

### 📊 Visualización recomendada
Integridad:
| Ruta | Estado | Último escaneo | 
| /etc/shadow | OK | 24/07/2025 08:00 | 
| /tmp/prueba.txt | Alterado | 24/07/2025 08:03 | 


### Alertas:
| Tipo | IP origen | Timestamp | Acción tomada | 
| DDOS DNS | 192.168.0.14 | 24/07/2025 07:45:11 | Bloqueada vía iptables | 

