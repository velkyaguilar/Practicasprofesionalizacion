from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'appsecretkey'  # Clave para sesiones

# ----------------- CONFIGURACIÓN DE MySQL -----------------
app.config['MYSQL_HOST'] = 'bqkqp63to4xfvbk536if-mysql.services.clever-cloud.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'up020ehktlnvhkkx'
app.config['MYSQL_PASSWORD'] = 'EZ55F2TJG6denuXNoEx1'
app.config['MYSQL_DB'] = 'bqkqp63to4xfvbk536if'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ----------------- RUTA PRINCIPAL -----------------
@app.route('/')
def index():
    return render_template('index.html')

# ----------------- LOGIN -----------------
@app.route('/accesologin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            try:
                # Verifica con hash
                valid = pbkdf2_sha256.verify(password, user['password'])
            except ValueError:
                # Si el password no está hasheado (usuarios antiguos)
                valid = (password == user['password'])

            if valid:
                session['logueado'] = True
                session['id'] = user['id']
                session['id_rol'] = user['id_rol']
                if user['id_rol'] == 1:
                    return render_template('admin.html')
                else:
                    return render_template('usuario.html')
        
        return render_template('login.html', error='Usuario o contraseña incorrectos')

    return render_template('login.html')

    

# ----------------- LOGOUT -----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

    

# ----------------- LISTAR PERSONAS -----------------
@app.route('/listar')
def listar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM persona")
    usuarios = cur.fetchall()
    cur.close()
    return render_template("listar.html", usuarios=usuarios) 

# ----------------- CRUD USUARIOS -----------------
@app.route('/listarUsuario', methods=['GET', 'POST'])
def listarUsuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        # Encriptar antes de guardar
        hash_password = pbkdf2_sha256.hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, '2')",
            (nombre, email, hash_password)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('listarUsuario'))

    # GET: mostrar lista
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

        # Encriptar nueva contraseña
        hash_password = pbkdf2_sha256.hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE usuario SET nombre = %s, email = %s, password = %s WHERE id = %s",
            (nombre, email, hash_password, id)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})

    except Exception as e:
        print("Error al actualizar:", e)
        return jsonify({'success': False, 'message': 'Error interno al actualizar'})

# ----------------- CRUD ADOPTANTES -----------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        raza = request.form.get('raza', '')
        fecha_adopcion = request.form.get('fecha_adopcion')  # Usar .get para evitar errores si no está presente
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO adoptante (nombre, email, raza, fecha_adopcion) VALUES (%s, %s, %s, %s)",
                (nombre, email, raza, fecha_adopcion)
            )
            mysql.connection.commit()
            cursor.close()
            
            flash('Adoptante registrado exitosamente', 'success')
            return redirect(url_for('registro'))
            
        except Exception as err:
            flash(f'Error al registrar adoptante: {err}', 'error')
            return redirect(url_for('registro'))
    
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM adoptante ORDER BY id_adoptante DESC")
        adoptantes = cursor.fetchall()
        cursor.close()

        return render_template('registro.html', adoptantes=adoptantes)

@app.route('/updateAdoptante', methods=['POST'])
def updateAdoptante():
    try:
        id_adoptante = request.form['id_adoptante']
        nombre = request.form['nombre']
        email = request.form['email']
        raza = request.form.get('raza', '')
        fecha_adopcion = request.form.get('fecha_adopcion')
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE adoptante SET nombre = %s, email = %s, raza = %s, fecha_adopcion = %s WHERE id_adoptante = %s",
            (nombre, email, raza, fecha_adopcion, id_adoptante)
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

# ----------------- CREAR USUARIO (registro desde formulario) -----------------
@app.route('/crearusuario', methods=['POST'])
def crearusuario():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    
    # Encriptar la contraseña antes de guardar
    hash_password = pbkdf2_sha256.hash(password)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, '2')",
        (nombre, email, hash_password)
    )
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('login'))

# ----------------- PÁGINAS DE INFORMACIÓN -----------------
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/admin')
def admin():
    cursor = mysql.connection.cursor()

    # Contar total de usuarios
    cursor.execute("SELECT COUNT(*) AS total FROM usuario")
    total_usuarios = cursor.fetchone()['total']

    # Contar total de adoptantes
    cursor.execute("SELECT COUNT(*) AS total FROM adoptante")
    total_adopciones = cursor.fetchone()['total']

    cursor.close()

    return render_template('admin.html',
                           total_usuarios=total_usuarios,
                           total_adopciones=total_adopciones)


@app.route('/listarAdop', methods=['GET'])
def listarAdop():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_adoptante, nombre, email, raza, fecha_adopcion FROM adoptante ORDER BY id_adoptante DESC")
    adoptantes = cursor.fetchall()
    cursor.close()

    return render_template('listarAdop.html', adoptantes=adoptantes)

    

# ----------------- INICIO APP -----------------

if __name__ == '__main__':
    app.run(debug=True, port=8000)
