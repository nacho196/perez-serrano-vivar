from flask import Flask, session, render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
import re

app = Flask(__name__)

mysql = MySQL()
app.secret_key = 'your secret key'

#Configuracion MySQL
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'final'

mysql.init_app(app)

@app.route('/')
def productos():
    sql="SELECT * FROM productos;"
    conn=mysql.connect() #Hacemos la conexion a mysql
    cursor=conn.cursor()
    cursor.execute(sql) #Ejecutamos el string sql
    
    rows=cursor.fetchall()
    print(rows)

    conn.commit()
    return render_template('productos.html',productos=rows) # Renderizo la pagina index.html

@app.route('/login', methods = ['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username_form = request.form['username']
        password_form = request.form['password']
   
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM usuarios WHERE username = %s;", [username_form])
        if cursor.fetchone()[0]:
            cursor.execute("SELECT password FROM usuarios WHERE username = %s;", [username_form])
            for row in cursor.fetchall():
                if password_form == row[0]:
                    session['usuario'] = username_form 
                    msg ="Se ha identificado correctamente"
                    return redirect('/')
                else:
                    msg = "Credenciales no validas"
        return render_template('login.html', msg=msg)
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

@app.route('/register', methods = ['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = %s', (username, ))
        user = cursor.fetchone()
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO usuarios VALUES (NULL,%s,%s,%s)',(username, password, email, ))
            conn.commit()
            #mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('login.html', msg=msg) 
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg = msg)

@app.route('/add', methods=['POST'])
def add_product_to_cart():
    # Aca debemos hacer una validacion para no permitir que usuarios no indenficados generen ordenes de pedido
    if 'usuario' not in session:
        msg = 'Debe iniciar sesion para continuar'
        return render_template('login.html', msg=msg)
        #msg = 'Su producto ha sido a;adido al carrito'
        #return redirect('/')
    else:
        msg = 'Su producto ha sido a;adido al carrito'
        return redirect('/')
        #msg = 'Debe iniciar sesion para continuar'
        #return render_template('login.html', msg=msg)
if __name__ == '__main__':
    app.run(debug=True)