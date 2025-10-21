from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from pprint import pprint   

app = Flask(__name__)
app.secret_key = 'appsecretkey'  # Clave para sesiones

# Configuración de MySQL
# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'informacion1'
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

# Listar usuarios
@app.route('/listar')
def listar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM persona")
    usuarios = cur.fetchall()
    cur.close()
    return render_template("listar.html", usuarios=usuarios) 

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# RUTAS PARA USUARIOS (CRUD)
@app.route('/listarUsuario', methods=['GET', 'POST'])
def listarUsuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, '2')",
            (nombre, email, password)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('listarUsuario'))

    # GET: mostrar lista de usuarios
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, email, password FROM usuario ORDER BY id ASC")
    listarUsuarios = cursor.fetchall()
    cursor.close()

    return render_template('listarUsuario.html', usuarios=listarUsuarios)

@app.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})

@app.route('/updateUsuario', methods=['POST'])
def updateUsuario():
    try:
        id = request.form['id']
        nombre = request.form['nombre'] 
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE usuario SET nombre = %s, email = %s, password = %s WHERE id = %s",
            (nombre, email, password, id)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })

    except Exception as e:
        print("Error al actualizar:", e)
        return jsonify({
            'success': False,
            'message': 'Error interno al actualizar'
        })

# RUTAS PARA ADOPTANTES (CRUD)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Agregar nuevo adoptante
        nombre = request.form['nombre']
        email = request.form['email']
        raza = request.form.get('raza', '')
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO adoptante (nombre, email, raza) VALUES (%s, %s, %s)",
                (nombre, email, raza)
            )
            mysql.connection.commit()
            cursor.close()
            
            flash('Adoptante registrado exitosamente', 'success')
            return redirect(url_for('registro'))
            
        except Exception as err:
            flash(f'Error al registrar adoptante: {err}', 'error')
            return redirect(url_for('registro'))
    
    else:
        # GET: Mostrar lista de adoptantes
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM adoptante ORDER BY id_adoptante DESC")
        adoptantes = cursor.fetchall()
        cursor.close()
        
        # Convertir a lista de diccionarios para mayor compatibilidad
        lista_adoptantes = []
        for adoptante in adoptantes:
            lista_adoptantes.append({
                'id_adoptante': adoptante['id_adoptante'],
                'nombre': adoptante['nombre'],
                'email': adoptante['email'],
                'raza': adoptante.get('raza', '')
            })
        
        return render_template('registro.html', adoptantes=lista_adoptantes)

@app.route('/updateAdoptante', methods=['POST'])
def updateAdoptante():
    try:
        id_adoptante = request.form['id_adoptante']
        nombre = request.form['nombre']
        email = request.form['email']
        raza = request.form.get('raza', '')
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE adoptante SET nombre = %s, email = %s, raza = %s WHERE id_adoptante = %s",
            (nombre, email, raza, id_adoptante)
        )
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Adoptante actualizado correctamente'})
        
    except Exception as err:
        return jsonify({'success': False, 'message': f'Error al actualizar: {err}'})

@app.route('/eliminar_adoptante/<int:id>', methods=['DELETE'])
def eliminar_adoptante(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM adoptante WHERE id_adoptante = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Adoptante eliminado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/listarAdop', methods=['GET', 'POST'])
def listarAdop():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        raza = request.form.get('raza', '')

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO adoptante (nombre, email, raza) VALUES (%s, %s, %s)",
            (nombre, email, raza)
        )
        mysql.connection.commit()
        cursor.close()
        
        flash('Adoptante registrado exitosamente', 'success')
        return redirect(url_for('listarAdop'))

    # GET: mostrar lista de adoptantes
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_adoptante, nombre, email, raza FROM adoptante ORDER BY id_adoptante DESC")
    adoptantes = cursor.fetchall()
    cursor.close()

    # Convertir a formato adecuado para DataTables
    lista_adoptantes = []
    for adoptante in adoptantes:
        lista_adoptantes.append({
            'id_adoptante': adoptante['id_adoptante'],
            'nombre': adoptante['nombre'],
            'email': adoptante['email'],
            'raza': adoptante.get('raza', 'No especificada')
        })

    return render_template('listarAdop.html', adoptantes=lista_adoptantes)

if __name__ == '__main__':
    app.run(debug=True, port=8000)