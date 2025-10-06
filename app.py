from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from pprint import pprint   

app = Flask(__name__)
app.secret_key = 'appsecretkey'  # Clave para sesiones

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'informacion'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# LOGIN
@app.route('/accesologin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['logueado'] = True
            session['id'] = user['id']
            session['id_rol'] = user['id_rol']
            if user['id_rol'] == 1:
                return render_template('admin.html')
            else:
                return render_template('usuario.html')
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')



# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/adoptantes')
def adoptantes_index():
    return render_template('adoptantes/index.html')

@app.route('/reportes')
def reportes_index():
    return render_template('reportes/index.html')

@app.route('/mascotas')
def mascotas_index():
    return render_template('mascotas/index.html')

@app.route('/registro/adoptante')
def registro_adoptante():
    return render_template('adoptantes/registro.html')

@app.route('/perro')
def registro_perro():
    return render_template('mascotas/registro.html')

@app.route('/regisAdop')
def regisAdop():
    return render_template('regisAdop.html')

@app.route('/lista/perros')
def lista_perros():
    return render_template('mascotas/lista.html')

@app.route('/mascotas')
def mascotas_listar():
    return render_template('mascotas_listar.html')

@app.route('/mascotas/agregar')
def mascotas_agregar():
    return render_template('mascotas_agregar.html')


# REGISTRO - Muestra el formulario
@app.route('/registro')
def registro():
    return render_template('registro.html')

# CREAR USUARIO - Procesa el formulario
@app.route('/crearusuario', methods=['POST'])
def crearusuario():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, '2')",
                   (nombre, email, password))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('login'))


# PÁGINAS DE INFORMACIÓN
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)