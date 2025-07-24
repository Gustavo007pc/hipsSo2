# HIPS
## Alumno: Christian Arce

Puntos cubridos por el hips:

 - Verificar archivos binarios de sistema y en particular modificaciones realizadas
en el archivo /etc/passwd o /etc/shadow.
 - Verificar los usuarios conectados al sistema y sus respectivos origenes.
 - Verificar si hay posibles sniffers en el sistema:
 - Se examinan los logs del sistema en busca de patrones de accesos indebidos. Los logs examinados son:
	 - /var/log/secure
	 - /var/log/messages
	 - /var/log/httpd/access_log
	 - /var/log/maillog
 - Se verifica el tamaño de la cola de mail en busca de envios de correos masivos desde una misma direccion.
 - Se verifican el uso de los recursos del sistema.
 - Se verifica la existencia de archivos sospechosos en el directorio /tmp.
 - Se verifican ataques ddos.
 - Se verifica la existencia de archivos en ejecucion como cron.
 - Se verifican intentos de accesos indebidos al sistema.
 

### El hips fue construido con:

 - Python
 - Flask
 - PostgreSQL


##  Pre-requisitos

#### Del sistema:

 - Centos 9 STREAM (ultima version estable)
 - Tener acceso como usuario root

#### Python3

Instalar instalar Python3 y Pip3
 
    sudo yum install python3
    sudo yum install python3-pip
    
##### Intalación de modulos de Python
    
Psycopg2
 

    pip3 install psycopg2

 Flask
 

    pip3 install flask
dotenv

    pip3 install python-dotenv

#### PostgreSQL
Instalar y configurar PostgreSQL


    sudo yum install postgresql
    sudo yum install postgresql-server
Inicializamos el cluster para poder configurar los archivos y configuracion necesaria

	sudo postgresql-setup --initdb

Iniciamos y habilitamos el servicio de postgres

    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    
##### Pasos para configurar la Base de Datos
Iniciamos con la cuenta de postgres

    sudo -i -u postgres

Creamos un nuevo rol

    create user hips with password 'password';
    
Creamos una base de datos

    createdb hips
    
Le asignamos los permisos necesarios al rol hips

    GRANT ALL PRIVILEGES ON DATABASE hips TO hips;
    
Creamos un usuario linux

    adduser hips
    
#### IPTables
Se para el servicio de firewalld

    sudo systemctl stop firewalld
Se desabilita

    sudo systemctl disable firewalld
Maskeamos para evitar que otro programa lo invoque

    sudo systemctl mask --now firewalld
Intalamos IPTables

    sudo yum install iptables-services -y
Iniciamos y habilitamos el servicio

    sudo systemctl start iptables
    sudo systemctl enable iptables
    sudo systemctl start ip6tables
    sudo systemctl enable ip6tables
Verificamos que este funcionando

    sudo systemctl status iptables
    sudo systemctl status ip6tables

#### Crontab

    sudo yum install cronie

## Instalacion

Descarga el programa en tu Desktop.

    git clone https:https://github.com/Christian-Arce/HIPS
Entra dentro del directorio y establece la contrasena que elegiste para la base de datos

    cd HIPS
    nano .env
    bd_password='contrasenha'
    bd_user='usuario'
    secret_key='secret_key'
    hips_email='correo del hips'
    hips_email_password='contrasenha del email del hips'
    hips_email_admin='email admin'

    
Guarda el archivo y cambia los permisos para que solo root pueda revisar el archivo

   

    sudo su
    chmod 700 .env


## Directorios Necesarios

Necesitamos crear algunos directorios donde el sistema guardara los resultados, las alarmas y los metodos de prevencion.

Estando como usuario root
      
        touch mkdir /var/log/hips/output/verificacion-cola-email/check_mailq.csv
        touch mkdir /var/log/hips/output/verificacion-logs/check_accessLog.csv
        touch mkdir /var/log/hips/output/verificacion-consumo/check_uso_alto.csv   
        touch mkdir /var/log/hips/output/verificacion-sniffers/check_sniffers.csv
        touch mkdir /var/log/hips/output/verificacion-cron/cron.csv        
        touch mkdir /var/log/hips/output/verificacion-ssh/check_ssh_logs.csv
        touch mkdir /var/log/hips/output/verificacion-ddos/check_ddos.csv    
        touch mkdir /var/log/hips/output/verificacion-tmp/check_tmp.csv
        touch mkdir /var/log/hips/output/verificacion-firma/verify_binaries.csv       
        touch mkdir /var/log/hips/output/verificacion-usuarios-conectados/check_users.csv


Crear los logs

    touch mkdir /var/log/hips/alarmas.log

    touch mkdir /var/log/hips/prevencion.log

    touch mkdir /var/log/message.log

    touch mkdir /var/log/secure.log

    touch mkdir /var/log/maillog.log

## Configurar sender_access para el bloqueo de emails
	sudo yum install postfix
	sudo systemctl start postfix
	sudo systemctl enable postfix
 Editar main.cf
 	
  	sudo nano /etc/postfix/main.cf
   	smtpd_recipient_restrictions = ..., check_sender_access hash:/etc/postfix/sender_access, ...
Crear sender_access

	mkdir /etc/postfix/sender_access
 Dar permisos

 	sudo chown root:postfix /etc/postfix/sender_access
	sudo chmod 644 /etc/postfix/sender_access


## Generar contrasenha hash para el administrador del hips

Ejecutar create_database.py para crear las tablas y guardar el usuario y los hashes
para /etc/passwd y /etc/shadow
    
## Modo de Uso
Estando como root en la carpeta HIPS

     export FLASK_APP=app
     flask run
En el navegador abre el siguiente link
   
    http://127.0.0.1:5000

usuario y contrasenha por defecto
admin , 12345



