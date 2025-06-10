from asyncio import gather
from os import getenv, path
from cx_Oracle import connect
import asyncio, requests, time

# Helpers
def execute(conn, query: str):
    # Execute Query
    cur = conn.cursor()
    cur.execute(query)
    # Parse to Dictionary
    data = [dict((cur.description[i][0], value)
        for i, value in enumerate(row)) for row in cur.fetchall()]
    # Return Data
    return data

#################################################################################################################################################

fileDir = path.dirname(path.abspath(__file__))
gusaapp_sql = path.abspath(path.join(fileDir, '../sql/furnace.gusaapp.sql'))

##########################################################################################################################
#                                                        MAIN CODE                                                       #
##########################################################################################################################

class db:

    def furnace():
        return connect(
            user='gusaapp',
            password='gusaapp',
            dsn='192.168.0.120/orcl',
            encoding='UTF-8'
        )

#################################################################################################################################################

async def gusaapp():
    try:
        # Connect to Server
        conn = db.furnace()
        # Execute Query
        data = execute(conn, open(gusaapp_sql).read())
        # Return Data
        return (True, data[0])
    except Exception as error:
        return (False, error)

#################################################################################################################################################

def get_from_iba(node):
    node = 'https://192.168.17.39:3002/api/ibalam/' + node
    try:
        return requests.get(node, verify=False).json()['data']['value']
    except:
        return 0

async def get_util():
    try:
        (
            (util),
            (time_util),
            (time_plc)
        ) = (
            get_from_iba('ns=3;s=V:0.3.0.0.5'),
            get_from_iba('ns=3;s=V:0.3.2.0.25'),
            get_from_iba('ns=3;s=V:0.3.2.0.26')
        )
        
        # Check Response
        # Update Data
        stop = (time_plc - time_util) / 60
        data = {
            'UTIL': util/100,
            'TEMPO_PARADO': stop
        }
        # Return Data
        return (True, data)
    except Exception as error:
        return (False, error)

#################################################################################################################################################

async def forno():
    try:
        data = {}
        (
            (ok1, furnace),
            (ok2, util)
        ) = await gather(
            gusaapp(),
            get_util()
        )
        # Check Response
        if not ok1: raise furnace
        if not ok2: raise util
        # Update Data
        data.update(furnace)
        data.update(util)
        # Return Data
        return (data)
    except Exception as error:
        return (error)