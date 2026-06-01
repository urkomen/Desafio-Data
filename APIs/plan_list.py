import flask
from flask import request, jsonify

# Diccionario de planes
plans = [
    {
        'id': 0,
        'title': 'Azkuna Zentroa – Alhóndiga Bilbao',
        'location': 'Bilbao, Bizkaia',
        # 'province': 'Bizkaia',
        'child_age_range': 'Todos los públicos',
        'rating': 4.5,
        'duration': '1h',
        'needs': {
            'Carrito':'Sí',
            'Interior':'Sí',
            'Cambiador':'Sí',
            'Precio':'Gratis (espacio público)'
            },
        'tags': ['Destacado','Gratis','Oferta activa'],
        'offers':[
            {
                'title':'2x1 en menú infantil',
                'date':'31 de octubre',
                'info':'Solo disponible los domingos. Imprescindible presentar app.'
            }
        ]
    },
    {
        'id': 1,
        'title': 'Parque infantil cubierto',
        'location': 'Bilbao, Bizkaia',
        # 'province': 'Bizkaia',
        'child_age_range': 'Todos los públicos',
        'rating': 3.6,
        'duration': '2h',
        'needs': {
            'Carrito':'Sí',
            'Interior':'Sí',
            'Cambiador':'Sí',
            'Precio':'Gratis'
        },
        'tags': ['Destacado','Gratis'],
        'offers':[]
    },
    {
        'id': 2,
        'title': 'Kutxa Ekogunea',
        'location': 'Donostia, Gipuzkoa',
        # 'province': 'Bizkaia',
        'child_age_range': 'Todos los públicos',
        'rating': 4.2,
        'duration': '2h',
        'needs': {
            'Carrito':'Sí',
            'Interior':'Sí',
            'Cambiador':'Sí',
            'Precio':'Gratis'
        },
        'tags': [],
        'offers':[]
    },
    {
        'id': 3,
        'title': 'Bizkaia Park Abentura',
        'location': 'Güeñes, Bizkaia',
        # 'province': 'Bizkaia',
        'child_age_range': 'Todos los públicos',
        'rating': 4.1,
        'duration': '1h',
        'needs': {
            'Carrito':'Sí',
            'Interior':'Sí',
            'Cambiador':'Sí',
            'Precio':'Gratis'
        },
        'tags': [],
        'offers':[]
    },
    {
        'id': 4,
        'title': 'Parque Natural de Gorbeia',
        'location': 'Sarria, Araba',
        # 'province': 'Bizkaia',
        'child_age_range': 'Todos los públicos',
        'rating': 4.9,
        'duration': '4-6h',
        'needs':{
            'Carrito':'Sí',
            'Interior':'No',
            'Cambiador':'Sí',
            'Precio':'Gratis'
        },
        'tags': [],
        'offers':[]
    },
    {
        'id': 5,
        'title': 'Reserva de la Biosfera de Urdaibai',
        'location': 'Urdaibai, Bizkaia',
        # 'province': 'Bizkaia',
        'child_age_range': 'Todos los públicos',
        'rating': 2.8,
        'duration': '2-4h',
        'needs': {
            'Carrito':'Parcial',
            'Interior':'No',
            'Cambiador':'No',
            'Precio':'10 €'
        },
        'tags': ['Oferta activa'],
        'offers':[
            {
                'title':'Entrada gratis menores de 8 años',
                'date':'12 de julio',
                'info':'De lunes a viernes, excepto festivos y vísperas de festivo. Imprescindible presentar app.'
            }
        ]
    }]






app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>TxikiPlan</h1><p>Esta web devuelve planes</p>`"

@app.route('/api/v1/resources/plans/all', methods=['GET'])
def api_all():
    return jsonify(plans)

@app.route('/api/v1/resources/plan', methods=['GET'])
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    results = []

    for plan in plans:
        if plan['id'] == id:
            results.append(plan)

    return jsonify(results)


app.run()