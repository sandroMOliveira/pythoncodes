#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyodbc
import datetime
import logging
from math import sqrt
from time import sleep
from triangulacao import triangulacao
from intersecao_de_pontos import Intersecao_de_pontos
from calculo_distancia import calculo_distancia


usuario_senha = 'DSN=beacon;UID=sa;PWD=r13r13r13'
connection = pyodbc.connect(usuario_senha)
cursor = connection.cursor()
numero_de_ultimas_leituras = ''
logging.basicConfig(filename='situacao_historico.log',
	level=logging.INFO,
	format='%(levelname)s %(module)s: %(message)sData: %(asctime)s.%(msecs)02d\n',
	datefmt="%d/%m/%Y %H:%M:%S")



def verifica_numero_de_receptores(vetor_id_receptores, beacon_especifico):
	receptores = []
	for beacon in beacon_especifico:
		for id_receptor in vetor_id_receptores:
			if id_receptor == beacon[2]:
				if id_receptor not in receptores:
					receptores.append(id_receptor)
	# retorna um array com os ultimos receptores que leram o beacon especifico.
	# eliminando receptores repetidos
	# exemplo: [3,3,2,1,3,2,1,1,2,3]
	# retorna: [1,2,3]
	return receptores



def remove_receptores_repetidos_e_retorna_menor_raio(id_de_receptores, raios):
	menor = []
	for ids in id_de_receptores:
		menor.append(sorted(list(filter(lambda x : x[0] == ids, raios)), key=lambda x : x[2])[0])
	return menor



def pontos_e_raios(id_de_receptores, beacon_especifico):
	raios = []
	for beacon in beacon_especifico:
		# beacon_especifico
		# posicao na lista:
		# 4 id_beacon
		# 5 rssi
		# 6 referencia_calibracao
		# 10 id_ambiente
		# 13 posicao_x
		# 14 posicao_y

		# calcular o raio dos receptores ate o beacon
		# calculo retorna em metros: multiplica por 100 para ficar em centimetros
		distancia = round(calculo_distancia(beacon[5], beacon[6])*100)

		# salvando: id_receptor, id_ambiente, distancia, posicao X, posicao Y, id_beacon
		raios.append([beacon[2], beacon[10], distancia, beacon[13], beacon[14], beacon[4]])
	
	raios = remove_receptores_repetidos_e_retorna_menor_raio(id_de_receptores, raios)
	# se 3 ou mais receptores leram o beacon
	if len(id_de_receptores) >= 3:
		# calcula triangulacao
		(posicao_x, posicao_y) = triangulacao(raios)
	# se apenas 2 receptores leram o beacon
	elif len(id_de_receptores) == 2:
		# calcula a interseccao entre dois circulos e acha o ponto onde se encontram
		interseccao = Intersecao_de_pontos(raios)
		# se encontra a interseccao, ou seja, é retornado um array
		if type(interseccao) == list:
			for index, _ in enumerate(interseccao):
				posicao_x = interseccao[index].real
				posicao_y = interseccao[index].imag
		else:
			# caso nao consiga achar a interseccao
			# verifica qual receptor esta mais proximo do beacon e pega
			# sua posicao x,y para que o beacon esteja na mesma posicao
			(posicao_x, posicao_y) = verifica_receptor_mais_proximo_do_beacon(raios)
	else:
		(posicao_x, posicao_y) = verifica_receptor_mais_proximo_do_beacon(raios)
	return posicao_x, posicao_y



def verifica_receptor_mais_proximo_do_beacon(raios):
	# list comprehension para pegar menor raio dentro do vetor raios
	menor = min([raio[2] for raio in raios])
	posicao_x = None
	posicao_y = None
	# raios [id_receptor, id_ambiente, distancia, posicao X, posicao Y, id_beacon]
	for index, raio in enumerate(raios):
		if raio[2] == menor:
			posicao_x = raios[index][3]
			posicao_y = raios[index][4]
	return posicao_x, posicao_y



def inserir_na_tabela_beacon_situacao():
	# buscar beacons cadastrados no banco
	beacons_cadastrados = select_no_banco('beacon')
	
	receptores = select_no_banco('receptor') # receptores cadastrados no banco
	vetor_id_receptores = [v[0] for v in receptores] # pegar id dos receptores

	for beacon in beacons_cadastrados:
		beacon_especifico = select_especifico(beacon[0]) # busca as ultimas leituras do beacon
		numero_de_id_receptores = verifica_numero_de_receptores(vetor_id_receptores, beacon_especifico)
		(posicao_x, posicao_y) = pontos_e_raios(numero_de_id_receptores, beacon_especifico)

		data = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'), '%Y-%m-%dT%H:%M:%S.%f')
		id_beacon = beacon_especifico[0][4]
		id_ambiente = beacon_especifico[0][10]
		nivel_bateria = beacon_especifico[0][7]

		# salvar no beacon_situacao:
		sql = "UPDATE beacon_situacao SET id_beacon = (?), id_ambiente = (?), data = (?), posicao_x = (?), posicao_y = (?), nivel_bateria = (?) WHERE id_beacon = "+str(id_beacon)+""
		cursor.execute(sql, (id_beacon, id_ambiente, data, posicao_x, posicao_y, nivel_bateria))
		cursor.commit()

		# salvar no beacon_historico:
		sql = "INSERT INTO beacon_historico (id_beacon, id_ambiente, data, posicao_x, posicao_y, nivel_bateria) VALUES (?,?,?,?,?,?)"
		cursor.execute(sql, (id_beacon, id_ambiente, data, posicao_x, posicao_y, nivel_bateria))
		cursor.commit()
		print ('LOG')
		logging.info('\nId beacon: %s\nId ambiente: %s\nPosicao X: %s\nPosicao Y: %s\n',
			id_beacon,
			id_ambiente,
			posicao_x,
			posicao_y,
			)



def select_especifico(beacon):
	sql = "SELECT valor FROM configuracao WHERE nome = 'qtd-leituras-avaliadas'"
	cursor.execute(sql)
	numero_de_ultimas_leituras = cursor.fetchall()
	# select das ultimas leituras realizadas em um determinado beacon
	sql = "SELECT top("+numero_de_ultimas_leituras[0][0]+") * FROM leitura, leitura_beacon, rece	ptor WHERE leitura.id_leitura = leitura_beacon.id_leitura and leitura.id_receptor = receptor.id_receptor and leitura_beacon.id_beacon = "+ str(beacon) +" ORDER BY data DESC"
	cursor.execute(sql)
	return cursor.fetchall()


	
def select_ordenado_no_banco(tabela, ordem):
	sql = "SELECT * FROM " + tabela + " ORDER BY " + ordem + " DESC"
	cursor.execute(sql)
	return cursor.fetchall()



def select_no_banco(tabela):
	cursor.execute("SELECT * FROM " + tabela)
	return cursor.fetchall()



if __name__ == '__main__':
	while True:
		inserir_na_tabela_beacon_situacao()
		sleep(10) # espera 10 segundos antes de executar o codigo novamente
