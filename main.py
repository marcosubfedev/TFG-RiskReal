from flask import Flask, render_template, request, redirect, url_for, session, jsonify, session
import json, os, uuid
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def set_password(self, password):
        """
        Genera y almacena el hash de la contraseña.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica si la contraseña coincide con el hash almacenado.
        """
        return check_password_hash(self.password_hash, password)
    
class Resultados(db.Model):
    usuario = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    fecha = db.Column(db.DateTime, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)

def ruta_json(file):
     ruta= 'json\\'+ file
     SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
     json_url = os.path.join(SITE_ROOT, ruta) 
     return json_url
     
@app.route("/")
def inicio():
    """
    Renderiza la página principal.
    """
    return render_template('inicio.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Gestiona el registro de nuevos usuarios.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('registro.html', error='El usuario ya existe')

        new_user = User(id=1,username=username, email=email)
        new_user.set_password(password)
        

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('inicio'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('inicio'))

@app.route("/test/p<path:page>", methods=['GET', 'POST'])
def test_page(page):
    """
    Renderiza la página del test según el parámetro 'page'.
    """

    user_id = session.get('user_id')
    if not user_id:
        count = User.query.filter_by(username='invitado').count()
        if count == 0:
            invitado = User(id=1,username='invitado',email='example@gamil.com')
            invitado.set_password('soyelinvitado') 
            db.session.add(invitado)
            db.session.commit()
    
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        session['username'] = 'invitado'        
    
    user_data = session.setdefault(user_id, {'page_counter': 1, 'total_valor': 0})
    if user_data['page_counter'] == 5:
        user_data['page_counter'] = 1
        user_data['total_valor'] = 0
    page_counter = user_data['page_counter']
    
    if request.method == 'POST': 
        if 'anterior' in request.form:
            user_data['page_counter'] = max(1, user_data['page_counter'] - 1)
            session['page_counter'] = user_data['page_counter']
            return redirect(url_for('test_page', page=user_data['page_counter']))

        file = f'test1_p{user_data["page_counter"]}.json'
        json_url = ruta_json(file)

        with open(json_url, 'r') as json_file:
            data = json.load(json_file)

        if 'option' in request.form:
            selected_option = request.form['option']
            for option in data['opciones']:
                if option['nombre'] == selected_option:
                    user_data['total_valor'] += option['valor']
                    session['total_valor'] = user_data['total_valor']
                    break

            user_data['page_counter'] += 1
            session['page_counter'] = user_data['page_counter']
            

            if 'finish' in request.form or user_data['page_counter'] == 5:
                return redirect(url_for('resultado_page'))
            else:
                return redirect(url_for('test_page', page=user_data['page_counter']))

    file = f'test1_p{user_data["page_counter"]}.json'
    json_url = ruta_json(file)

    with open(json_url, 'r') as json_file:
        data = json.load(json_file)

    # Actualizar los datos del usuario en la sesión
    session[user_id] = user_data

    return render_template(f'test_p{page}.html', data=data, page_counter=page_counter)



@app.route("/resultado")
def resultado_page():
    total_valor = session.get('total_valor', 0)

    resultado = Resultados(usuario=session.get('username'), fecha=datetime.now(), puntuacion=total_valor)
    db.session.add(resultado)
    db.session.commit()
    return render_template('resultado.html', total_valor=total_valor)

@app.route("/usuarios")
def mostrar_usuarios():
    """
    Consulta y muestra todos los usuarios en HTML.
    """
    usuarios = User.query.all()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/resultados")
def mostrar_resultados():
    """
    Consulta y muestra todos los resultados en HTML.
    """
    # Consulta para obtener todos los resultados
    resultados = Resultados.query.all()
    
    return render_template("resultados.html", resultados=resultados)