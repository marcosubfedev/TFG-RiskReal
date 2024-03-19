from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

@app.route("/test/p<path:page>", methods=['GET', 'POST'])
def test_page(page):
    """
    Renderiza la página del test según el parámetro 'page'.
    """
    if 'page_counter' not in session:
        session['page_counter'] = 1
        session['total_valor'] = 0
    
    page_counter = session['page_counter']       
         
    if request.method == 'POST': 
        if 'anterior' in request.form:
            session['page_counter'] = max(1, session['page_counter'] - 1)
            return redirect(url_for('test_page', page=session['page_counter']))  
        
        file = f'test1_p{page_counter}.json'
        json_url = ruta_json(file)

        with open(json_url, 'r') as json_file:
            data = json.load(json_file)

        if 'option' in request.form:
            selected_option = request.form['option']
            for option in data['opciones']:
                if option['nombre'] == selected_option:
                    session['total_valor'] += option['valor']
                    break

            # Aumenta el contador de la página cuando se envía el formulario.
            session['page_counter'] += 1

            if 'finish' in request.form or session['page_counter'] == 5:
                # Si es la quinta página, redirige a la página de resultados.
                return redirect(url_for('resultado_page'))
            else:
                return redirect(url_for('test_page', page=page_counter+1))

    file = f'test1_p{page_counter}.json'
    json_url = ruta_json(file)

    with open(json_url, 'r') as json_file:
        data = json.load(json_file)

    return render_template(f'test_p{page}.html', data=data, page_counter=page_counter)


@app.route("/resultado")
def resultado_page():
    total_valor = session.get('total_valor', 0)  # Obtiene el total de valor seleccionado de la sesión.
    return render_template('resultado.html', total_valor=total_valor)