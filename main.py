from flask import Flask, render_template, request, redirect, url_for, session, jsonify, session
import json, os, uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

users = {'admin': 'adminsoy', 'prueba': 'usuario1234'}

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
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
        return redirect(url_for('login')) 
    
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
    total_valor = session.get('total_valor', 0)  # Obtiene el total de valor seleccionado de la sesión.
    return render_template('resultado.html', total_valor=total_valor)