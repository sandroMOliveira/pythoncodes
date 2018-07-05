#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import pyodbc
import sys
import logging
from time import sleep

usuario_senha = 'DSN=beacon;UID=sa;PWD=r13r13r13'
connection = pyodbc.connect(usuario_senha)
cursor = connection.cursor()
logging.basicConfig(filename='bacon_localidade.log',
	level=logging.INFO,
	format='%(levelname)s %(module)s: %(message)sData: %(asctime)s.%(msecs)02d\n',
  datefmt="%d/%m/%Y %H:%M:%S")

def insert_ambiente_atual():
    beacons_ambiente = select_with_where()
    for beacons_ambiente in beacons_ambiente:
        id_beacon = beacons_ambiente[0]
        data = beacons_ambiente[1]
        id_item_monitorado = beacons_ambiente[2]
        desc = beacons_ambiente[3]
        id_ambiente = beacons_ambiente[4]
        desc_ambiente = beacons_ambiente[5]
        logging.info("\nId_beacon: %s\ndata_beacon: %s\nId_item_monitorado: %s\nDesc_Item: %s\nId_ambiente: %s\nDesc_ambiente: %s\n",
        id_beacon,
        data,
        id_item_monitorado,
        desc,
        id_ambiente,
        desc_ambiente)
    sleep(5)
    insert_ambiente_atual()

def select_with_where():
    select = "SELECT top(100)beacon_historico.id_beacon, beacon_historico.data, beacon_item_monitorado.id_item_monitorado, item_monitorado.identificacao, beacon_historico.id_ambiente, ambiente.descricao "
    fromSql = "FROM beacon_historico, beacon_item_monitorado, item_monitorado, ambiente "
    where = "WHERE beacon_historico.id_beacon = beacon_item_monitorado.id_beacon and beacon_item_monitorado.id_item_monitorado = item_monitorado.id_item_monitorado and item_monitorado.id_ambiente = ambiente.id_ambiente ORDER BY data DESC"
    sql = select + fromSql + where
    cursor.execute(sql)
    return cursor.fetchall()
    
def select_geral_banco(tabela):
    cursor.execute("SELECT * FROM " + tabela)
    return cursor.fetchall()


if __name__ == '__main__':
    insert_ambiente_atual()

