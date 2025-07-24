from flask import Flask, render_template, request, redirect, url_for, session 
import psycopg2
import sys 
import subprocess 
sys.path.append('verificacion-binarios/')
import csv
import os
app = Flask(__name__) 
app.secret_key = 'secret' 
import create_database 
from dotenv import load_dotenv
load_dotenv()

def con_db():
    # Conexión a la base de datos PostgreSQL
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='hips',
            user=os.getenv('bd_user'),
            password=os.getenv('bd_password')
        )
        print("Conexión a la base de datos exitosa.")
        return conn  # Retorna la conexion si es exitosa
    except Exception as e:
        print("Error al conectarse a la base de datos:", e)
        return None  # Retorna nada si hay error

@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    if request.method == 'POST': 
        username = request.form['username'] 
        password = request.form['password'] 

        # Get the database connection from the session 
        conn = con_db() 
        cur = conn.cursor() 

        # Query the database for the user 
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password)) 
        user = cur.fetchall() 

        # Close the cursor (optional, but recommended) 
        cur.close() 
        conn.close() 

        if user: 
            return redirect(url_for('menu')) 
        else: 
            error = "Invalid credentials. Please try again." 
            return render_template('HIPS-login.html', error=error) 
    else: 
        return render_template('HIPS-login.html')

@app.route('/menu') 
def menu(): 
    return render_template('HIPS-web.html')

def input_csv(file_name):

    # Carga los datos del archivo CSV y retorna una lista de filas
    datos = []
    with open(file_name, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for fila in reader:
            datos.append(fila)
    return datos

@app.route('/<folder>/<program_name>')
def ejecutar_herramienta(folder,program_name):
    subprocess.run(["python3", f"./{folder}/{program_name}.py"])
    output = input_csv(f"/var/log/hips/output/{folder}/{program_name}.csv")
    return render_template('HIPS-output.html', output=output)


@app.route('/') 
def root(): 
    return redirect(url_for('login')) 


if __name__ == '__main__': 
    create_database.create_database()
    app.run(debug=True)