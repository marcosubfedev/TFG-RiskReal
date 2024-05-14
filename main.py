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
con_admin='RiskReal'

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_empresa = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False)
    nombre = db.Column(db.String(50), nullable=True)
    apellido = db.Column(db.String(50), nullable=True)
    genero = db.Column(db.String(50), nullable=True)
    edad = db.Column(db.Integer, nullable=True)
    rol = db.Column(db.String(50), nullable=True)
    CampoPr = db.Column(db.String(50), nullable=True)
    admin = db.Column(db.Boolean, default=False)
    camb_cont = db.Column(db.Boolean, default=False)


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
        cod_empresa = request.form['cod_empresa']
        email = request.form['email']
        password = request.form['password'] 
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        genero = request.form['genero']
        edad = request.form['edad']
        rol = request.form['rol']
        CampoPr = None
        admin = False
        camb_cont = False

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('registro.html', error='El correo ya existe')

        if 'admin' in request.form and request.form['admin'] == con_admin:
            admin=True
        
        new_user = User( cod_empresa=cod_empresa, email=email, nombre=nombre, apellido=apellido, genero=genero, edad=edad, rol=rol, CampoPr= CampoPr, admin=admin, camb_cont=camb_cont)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            nombre=user.nombre
            admin=user.admin
            email=user.email
            camb_cont = user.camb_cont
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
            session['nombre'] = nombre
            session['email'] = email
            session['admin'] = admin
            session['camb_cont'] = camb_cont
            return redirect(url_for('inicio'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@app.route('/boolcontraseña', methods=['GET', 'POST'])
def bool_contraseña():
    if request.method == 'POST':
        email = request.form['email']
        # Busca el usuario por su correo electrónico
        user = User.query.filter_by(email=email).first()
        if user:
            # Actualiza el valor de camb_cont a True
            user.camb_cont = True
            db.session.commit()
            return redirect(url_for('inicio'))
        else:
            return render_template('boolContraseña.html', error='No se encontró ningún usuario con ese correo electrónico')

    return render_template('boolContraseña.html')

@app.route('/cambiarcontraseña', methods=['GET', 'POST'])
def cambiar_contraseña():
    if request.method == 'POST':
        email = session.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if new_password != confirm_password:
                return render_template('cambiarContraseña.html', error='Las contraseñas no coinciden')

            camb_cont=False
            user.camb_cont = camb_cont
            user.set_password(new_password)
            db.session.commit()

            session.pop('user_id', None)
            session.pop('nombre', None)
            session.pop = ('email', None)
            session.pop = ('admin', None)
            session.pop = ('camb_cont', None)
            return redirect(url_for('login'))
        else:
            return render_template('cambiarContraseña.html', error='Usuario no encontrado')

    return render_template('cambiarContraseña.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('nombre', None)
    session.pop = ('email', None)
    session.pop = ('admin', None)
    session.pop = ('camb_cont', None)
    return redirect(url_for('inicio'))

@app.route("/esta_logeado")
def esta_logeado():
    test = request.args.get('test')
    if test == 'True':
        test = True
    elif test == 'False':
        test = False
    else:
        test = False
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('datos_invitado'))
    elif test:
        return redirect(url_for('test_page', page=1))
    else:
        return redirect(url_for('cuestionario_page', page=1))
    
@app.route("/invitado",  methods=['GET', 'POST'])
def datos_invitado():
    test = request.args.get('test', default=False, type=bool) 

    if request.method == 'POST':
        cod_empresa = 1234
        nombre='invitado'
        apellido = None
        edad = request.form['edad']
        rol = request.form['rol']
        genero = request.form['genero']
        CampoPr = request.form['CampoPr']
        admin = False
        camb_cont = False

        count = User.query.filter_by(nombre='invitado').count()
        if count == 0:
            invitado = User(cod_empresa=cod_empresa, email='example@gmail.com', nombre=nombre, apellido=apellido, genero=genero, edad=edad, rol=rol, CampoPr= CampoPr, admin=admin, camb_cont=camb_cont)
            invitado.set_password('soyelinvitado') 
            db.session.add(invitado)
        else:
            invitado = User.query.filter_by(nombre='invitado').first()
            invitado.genero = genero
            invitado.edad = edad
            invitado.rol = rol
            invitado.CampoPr = CampoPr

        db.session.commit()
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        session['nombre'] = 'invitado'  
        return redirect(url_for('test_page' if test else 'cuestionario_page', page=1))
    
    return render_template('datosInvitado.html')

@app.route("/test/p<path:page>", methods=['GET', 'POST'])
def test_page(page):
    """
    Renderiza la página del test según el parámetro 'page'.
    """
    
    user_id = session.get('user_id')        
    user_data = session.setdefault(user_id, {'page_counter': 1, 'total_valor': 0})
    
    file = 'test_1.json'
    json_url = ruta_json(file)
    with open(json_url, 'r') as json_file:
        combined_data = json.load(json_file)
        paginas = combined_data.get('paginas', 1)

    if request.method == 'POST': 
        if 'anterior' in request.form:
            user_data['page_counter'] = max(1, user_data['page_counter'] - 1)
            session['page_counter'] = user_data['page_counter']
            return redirect(url_for('test_page', page=user_data['page_counter']))

        selected_option = request.form.get('option')
        for option in combined_data.get(page, {'opciones': []})['opciones']:
            if option['nombre'] == selected_option:
                user_data['total_valor'] += option['valor']
                session['total_valor'] = user_data['total_valor']
                break

        user_data['page_counter'] += 1
        session['page_counter'] = user_data['page_counter']
        
        if 'finish' in request.form or user_data['page_counter'] > paginas:
            session.pop(user_id, None)
            return redirect(url_for('resultado_page'))
        else:
            return redirect(url_for('test_page', page=user_data['page_counter']))


    data = combined_data.get(page, {'opciones': []})

    session[user_id] = user_data

    return render_template(f'test_escenario.html', data=data, page_counter=user_data['page_counter'],paginas=paginas)

@app.route("/cuestionario/p<path:page>", methods=['GET', 'POST'])
def cuestionario_page(page):
    """
    Renderiza la página del cuestionario según el parámetro 'page'.
    """
    user_id = session.get('user_id')        
    user_data = session.setdefault(user_id, {'page_counter': 1, 'total_valor': 0})
    
    file = 'cuestionario_1.json'  
    json_url = ruta_json(file)
    with open(json_url, 'r') as json_file:
        combined_data = json.load(json_file)
        paginas = len(combined_data)

    if request.method == 'POST': 
        if 'anterior' in request.form:
            user_data['page_counter'] = max(1, user_data['page_counter'] - 1)
            session['page_counter'] = user_data['page_counter']
            return redirect(url_for('cuestionario_page', page=user_data['page_counter']))

        selected_option = request.form.get('opcion')
        if selected_option:
            selected_option = float(selected_option)
            user_data['total_valor'] += selected_option
            session['total_valor'] = user_data['total_valor']
        user_data['page_counter'] += 1
        session['page_counter'] = user_data['page_counter']
        
        if 'finish' in request.form or user_data['page_counter'] > paginas:
            session.pop(user_id, None)
            return redirect(url_for('resultado_page'))
        else:
            return redirect(url_for('cuestionario_page', page=user_data['page_counter']))


    data = combined_data.get(page, {})
    session[user_id] = user_data

    return render_template(f'cuestionario.html', data=data, page_counter=user_data['page_counter'],paginas=paginas)

@app.route("/resultado")
def resultado_page():
    total_valor = session.get('total_valor', 0)

    resultado = Resultados(usuario=session.get('nombre'), fecha=datetime.now(), puntuacion=total_valor)
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