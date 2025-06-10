from datetime import datetime, date, timedelta
from modules import Homerico
from flask import jsonify
from io import StringIO
import pandas as pd
import numpy as np
import time, json, requests

username = ''
password = ''
company = ''
registros = {}


def check_null(var):
    if (not var): raise Exception('A variável {} não pode ser vazia'.format(var))

def validation(company):
    print('''
            _____  _____   _                 __  __ 
     /\    |  __ \|_   _| | |         /\    |  \/  |
    /  \   | |__) | | |   | |        /  \   | \  / |
   / /\ \  |  ___/  | |   | |       / /\ \  | |\/| |
  / ____ \ | |     _| |_  | |____  / ____ \ | |  | |
 /_/    \_\|_|    |_____| |______|/_/    \_\|_|  |_|
                                                    
                                                    
          POWERED BY AÇO VERDE DO BRASIL S/A
''')
    check_null(company)
    print('VALIDANDO {}'.format(company.upper()))
    VALIDACAO = json.loads(Homerico.Validar(company))
    if(int(VALIDACAO['status']) != 1): raise Exception('ERRO NA VALIDAÇÃO PARA {}'.format(company.upper()))
    print(VALIDACAO['msg'].upper(), end= '\n\n')

def login(username, password):
    check_null(username)
    check_null(password)
    print('CONECTANDO COM USUÁRIO {} E SENHA {}'.format(username.upper(), password.upper()))
    LOGIN = json.loads(Homerico.Login(username, password))
    if(int(LOGIN['status']) != 1): raise Exception('ERRO NO LOGIN PARA USUÁRIO {} E SENHA {}'.format(username.upper(), password.upper()))
    print(LOGIN['msg'].upper(), end= '\n\n')

# GET START AND END DATE OF TRIMESTRE
def trimStartEndDates( month: int, now: datetime ) -> tuple[str, str]:
    if month > now.month: return (None, None)
    day = (
        now.day if month == now.month else
        lastDayOfMonth(date(now.year, month, 1)).day
    )
    sdate = date(now.year, month, 1)
    edate = date(now.year, now.month, day)
    return (sdate, edate)

# GET LAST DAY OF MONTH
def lastDayOfMonth(date: datetime):
    return date.replace(day=31) if date.month == 12 else date.replace(month=(date.month + 1), day=1) - timedelta(days=1)

# PARSE STRING TO INT/FLOAT
def checkTypeNumber(numero):
    return int(float(numero)) if isinstance(numero, (int, np.integer)) else float(numero.replace(',', '.'))

# REPLACE NAN VALUES TO 0 IN PANDAS
def replaceNaNValues(number):
    return number if str(number) != str(np.nan) else int(str(number).replace(str(np.nan), '0'))

# GET REGISTRO IN HOMERICO
def get_registro(datas, registro):
    x, day, metaD = 0, 0, 0
    final = datas[1].strftime("%d/%m/%Y")
    if datas[1].month == datetime.now().date().month:
        final = datetime.now().date().strftime("%d/%m/%Y")
    df = pd.read_csv(StringIO(Homerico.RelatorioGerencialRegistro("{}".format(final), str(registro))), sep = ";").filter(['registro','meta','dia','acumulado'])
    try:
        x = checkTypeNumber(replaceNaNValues(df['acumulado'][0]))
        day = checkTypeNumber(replaceNaNValues(df['dia'][0]))
        metaD = checkTypeNumber(replaceNaNValues(df['meta'][0]))
    except:
        pass
    x = x if x > 0 else 0
    return {'total':x, 'dia':day,'meta':metaD}

# GET LIST OF PRODUCTION
def pegaLista(registro):
    now = datetime.now()
    final = datetime.now().date().strftime("%d/%m/%Y")
    csv_file = (StringIO(Homerico.ProducaoLista("{}".format(final), str(registro))))
    df = pd.read_csv(csv_file, sep = ";")
    try:
        df = df.filter(['data','peso'])
        lista = {}
        for i in range(1, now.day+1):
            df['data'] = df['data'].replace([i],"{0:-02d}/m/y".format(i))
        df = df.stack().str.replace('m','{0:-02d}'.format(now.month)).unstack()
        df = df.stack().str.replace('y','{}'.format(now.year)).unstack()
        df = df.stack().str.replace(',','.').unstack()
        df['peso'].astype(float)
        df = df.to_dict(orient="records")
        return json.dumps(df)
    except:
        return {'data': 0, 'peso': 0};
        pass

# GET REGISTRO
def pegaIndicadores(registros):
    metas = {}
    check_null(registros)
    for registro in registros:
        now = datetime.now()
        tlst = dict[int, tuple[int, int, int]]
        trims: tlst = { 1: (1, 2, 3), 2: (4, 5, 6), 3: (7, 8, 9), 4: (10, 11, 12) }
        trim = trims[1 + ((now.month - 1) // 3)]
        helper = lambda m: (m, lastDayOfMonth(date(now.year, m, 1)))
        metaNow = get_registro(trimStartEndDates(now.month, now), str(registro))
        metas[str(registros[registro])] = {
            'acumulado': (metaNow['total']),
            'mes1': (get_registro(trimStartEndDates(*helper(trim[0])), str(registro))['total']),
            'mes2': (get_registro(trimStartEndDates(*helper(trim[1])), str(registro))['total']),
            'mes3': (get_registro(trimStartEndDates(*helper(trim[2])), str(registro))['total']),
            'dia':  (metaNow['dia']),
            'meta':  (metaNow['meta'])
        }
    return jsonify(metas)

# REQUESTS IBA
def get_from_iba(node):
    node = 'http://192.168.17.39:3002/api/ibalam/' + node
    return requests.get(node).json()['data']['value']