__version__ = '1.0.0'
import setup, os, requests,asyncio, requests, time
from flask import Flask, jsonify, render_template
from datetime import datetime
from modules import Homerico, gusaapp

app = Flask(__name__, template_folder='E:/api-lam-indicadores/templates')

# SETUP
username = 'CH1976'
password = 'iry3873'
company = 'homerico.avb'

setup.validation(company)
setup.login(username, password)
registros = {
    1444: "BLBP",           # Barras Laminadas/ Barras Perdidas
    1350: "SUCATEAMENTO",   # Sucateamento de Laminado
    1333: "ACIDENTE CPT",   # Acidente CPT
    1336: "PROD LAMINADO",  # Produção da Laminação
    3087: "REND. METALICO", # Rendimento Metálico do Laminado
    1456: "UTILIZACAO"      # Utilização do Laminador
}

last_req_meta = datetime(2010, 7, 6, 5, 27, 0, 0)
last_req_prod = datetime(2010, 7, 6, 5, 27, 0, 0)
last_req_blbp = datetime(2010, 7, 6, 5, 27, 0, 0)
last_req_rhf = datetime(2010, 7, 6, 5, 27, 0, 0)
last_meta = 0
last_prod = 0
last_blbp = 0
last_rhf = 0

# API CONFIGS
@app.route('/api/metas/')
def metas():
    global last_req_meta
    global last_meta
    now = datetime.now().replace(second=0, microsecond=0)
    if((last_req_meta < now)):
        print()
        print("PEGANDO META DA API, LAST {}, ACTUAL {}".format(last_req_prod, now))
        last_req_meta = now
        last_meta = setup.pegaIndicadores(registros)
        return last_meta
    print()
    print("PEGANDO ULTIMA META, LAST {}, ACTUAL {}".format(last_req_prod, now))
    return last_meta

@app.route('/api/producao/')
def ProdLista():
    global last_req_prod
    global last_prod
    now = datetime.now().replace(second=0, microsecond=0)
    if((last_req_prod < now)):
        print()
        print("PEGANDO PROD DA API, LAST {}, ACTUAL {}".format(last_req_prod, now))
        last_req_prod = now
        last_prod = setup.pegaLista('1269')
        return last_prod
    print()
    print("PEGANDO ULTIMA PROD, LAST {}, ACTUAL {}".format(last_req_prod, now))
    return last_prod

@app.route('/api/blbp/')
def BlbpLista():
    global last_req_blbp
    global last_blbp
    now = datetime.now().replace(second=0, microsecond=0)
    if((last_req_blbp < now)):
        print()
        print("PEGANDO BLBP DA API, LAST {}, ACTUAL {}".format(last_req_blbp, now))
        last_req_blbp = now
        last_blbp = setup.pegaLista('1444')
        return last_blbp
    print()
    print("PEGANDO ULTIMA BLBP, LAST {}, ACTUAL {}".format(last_req_blbp, now))
    return last_blbp

@app.route('/rhf/')
def rhf():
    global last_req_rhf
    global last_rhf
    now = datetime.now().replace(second=0, microsecond=0)
    if((last_req_rhf < now)):
        print()
        print("PEGANDO RHF DA API, LAST {}, ACTUAL {}".format(last_req_rhf, now))
        rhf = asyncio.run(gusaapp.forno())
        last_rhf = rhf
        last_req_rhf = now
        return jsonify(rhf)
    print()
    print("PEGANDO ULTIMO RHF, LAST {}, ACTUAL {}".format(last_req_rhf, now))
    return jsonify(last_rhf)

@app.route('/rhf/indicadores')
def indicadores():
    try:
        response = requests.get("http://192.168.17.61:3005/rhf/")
        data = response.json()
        boxes = [
            ("PEÇAS HORA ATUAL", round(data.get("ATUAL_HORA_PECAS", 0))),
            ("PESO HORA ATUAL", round(data.get("ATUAL_HORA_PESO", 0,), 1)),
            ("RITMO HORA", round(data.get("RITIMO_HORA", 0), 1)),
            ("UTILIZAÇÃO (%)", round(data.get("UTIL", 0) * 100)),
            ("PEÇAS ÚLTIMA HORA", round(data.get("ULTIMA_HORA_PECAS", 0))),
            ("PESO ÚLTIMA HORA", round(data.get("ULTIMA_HORA_PESO", 0), 1)),
            ("RITMO DIA", round(data.get("RITIMO_DIA", 0), 1)),
            ("TEMPO PARADO (min)", round(data.get("TEMPO_PARADO", 0))),
            ("QUANT. DIA", round(data.get("QTD_PECAS", 0))),
            ("PESO DIA", round(data.get("PESO_TOTAL", 0), 1)),
        ]

        return render_template('index.html', boxes=boxes)
    except Exception as e:
        error_message = "Erro ao obter dados da API: " + str(e)
        return render_template('index.html', error_message=error_message)

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 3005,
        debug=True
    )