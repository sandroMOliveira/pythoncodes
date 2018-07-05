#!/usr/bin/env python
# -*- coding: utf-8 -*-



import datetime
import pyodbc
import json
import sys
import logging
import paho.mqtt.client as mqtt



usuario_senha = 'DSN=beacon;UID=sa;PWD=r13r13r13'
connection = pyodbc.connect(usuario_senha)
cursor = connection.cursor()
logging.basicConfig(filename='leitura.log',
	level=logging.INFO,
	format='%(levelname)s %(module)s: %(message)sData: %(asctime)s.%(msecs)02d\n',
  datefmt="%d/%m/%Y %H:%M:%S")


def select_no_banco(tabela):
	cursor.execute("SELECT * FROM " + tabela)
	return cursor.fetchall()

def select_especifico_no_banco(beacon, receptor):
	# select que busca o ultimo rssi lido do beacon pelo receptor X 
	cursor.execute("SELECT TOP(1) rssi, id_receptor FROM leitura_beacon, leitura WHERE leitura_beacon.id_beacon = "+str(beacon)+" and leitura_beacon.id_leitura = leitura.id_leitura and leitura.id_receptor = "+str(receptor)+" ORDER BY leitura_beacon.id_leitura desc")
	return cursor.fetchall()


def encontra_id(vetor_mac, mac_address, vetor_id):
	# encontra o id do receptor pelo endereco mac dele
	for index, mac in enumerate(vetor_mac):
		if mac_address == mac:
			return vetor_id[index]



def salvar_dados_na_tabela_leitura_beacon(id_ultima_leitura, data, beacons_no_banco, id_receptor):
	cursor.execute("SELECT valor FROM configuracao")
	configuracao = cursor.fetchall()
	min_mudanca_raio = configuracao[1][0]

	vetor_mac_address_de_beacons = []
	vetor_id_de_beacons = []
	for beacon_no_banco in beacons_no_banco:
		vetor_mac_address_de_beacons.append(beacon_no_banco[2])
		vetor_id_de_beacons.append(beacon_no_banco[0])
	beacons_lidos = []
	# para cada beacon na leitura do receptor
	for raw_beacon_data in data['raw_beacons_data'].split(';'):
		if not raw_beacon_data:
			continue
		# se o beacon ja esta cadastrado no banco de dados
		if raw_beacon_data[0:12] in vetor_mac_address_de_beacons:
			if raw_beacon_data[54:56] == 'FF': # se o nivel de bateria é desconhecido (FF na leitura)
				nivel_bateria = "NULL"
			else:
				nivel_bateria = int('0x' + raw_beacon_data[54:56], 0)
			id_beacon = encontra_id(vetor_mac_address_de_beacons, raw_beacon_data[0:12], vetor_id_de_beacons)
			beacons_lidos.append(id_beacon)
			rssi = int('0x' + raw_beacon_data[56:58], 0) - 256
			beacon_data = {
				'id_leitura': id_ultima_leitura,
				# encontra o id do beacon pelo mac address
				'id_beacon': id_beacon,
				'rssi': rssi,
				'referencia_calibracao': int('0x' + raw_beacon_data[52:54], 0) - 256,
				'nivel_bateria': nivel_bateria,
			}
			buscar_ultimo_rssi_lido = select_especifico_no_banco(id_beacon, id_receptor)
			diferenca_de_rssi = abs(buscar_ultimo_rssi_lido[0][0] - rssi)
		if diferenca_de_rssi >= min_mudanca_raio:
			try:
				sql = "INSERT INTO leitura_beacon (id_leitura, id_beacon, rssi, referencia_calibracao, nivel_bateria) VALUES ({id_leitura}, {id_beacon}, {rssi}, {referencia_calibracao}, {nivel_bateria})".format(**beacon_data)
				cursor.execute(sql)
				cursor.commit()
			except Exception as e:
				print (e)
		else:
			print ('')
			# 	print 'min_mudanca_raio: ', min_mudanca_raio
			# 	print 'Diferenca pequena: beacon: ', id_beacon, '\nid_receptor: ', id_receptor, '\n'
	print ('LOG')
	logging.info('\nNova Leitura: %s\nId receptor: %s\nBeacons lidos: %s\n', id_ultima_leitura, id_receptor, beacons_lidos)



def salvar_dados_na_tabela_leitura(id_receptor, data, beacons_no_banco):
	# pega a hora atual
	data_hora = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'), '%Y-%m-%dT%H:%M:%S.%f')
	sql = "INSERT INTO leitura (id_receptor, data) VALUES (?,?)"
	try:
		cursor.execute(sql, (id_receptor, data_hora)) # cria no banco uma nova leitura
		cursor.commit()
		cursor.execute("SELECT @@IDENTITY") # busca do id desta ultima leitura cadastrada
		id_tabela_leitura = int(cursor.fetchall()[0][0]) # salva o id em uma variavel
		if id_tabela_leitura is not None: # se o id_tabela_leitura existe
			salvar_dados_na_tabela_leitura_beacon(id_tabela_leitura, data, beacons_no_banco, id_receptor)
	except Exception as e:
		print (e)



def on_message(client, userdata, message):
	data = json.loads(message.payload) # converte data para formato Json
	receptores_no_banco = select_no_banco('receptor')
	beacons_no_banco = select_no_banco('beacon')
	print (message.topic + " " + str(message.qos) + " " + str(message.payload))
	vetor_mac_address_de_receptores = []
	vetor_id_de_receptores = []
	for receptor_no_banco in receptores_no_banco:
		vetor_mac_address_de_receptores.append(receptor_no_banco[3]) # todos os mac_address de receptores cadastrados
		vetor_id_de_receptores.append(receptor_no_banco[0]) # todos os ids de receptores cadastrados

	mac_address_receptor = message.payload[7:19] # pega o mac address do receptor na mensagem lida (captura)

	if mac_address_receptor in vetor_mac_address_de_receptores: # verifica se o receptor que fez a captura de dados agora, esta cadastrado no banco de dados
	# se sim:
	# encontra o id do receptor no banco de dados pelo mac_address dele
		id_receptor = encontra_id(vetor_mac_address_de_receptores, mac_address_receptor, vetor_id_de_receptores)
		print ('id_receptor', id_receptor)
		if id_receptor is not None: # se encontrar o id 
			salvar_dados_na_tabela_leitura(id_receptor, data, beacons_no_banco)
	else:
		raise TypeError("Receptor nao cadastrado no banco de dados")
		
if __name__ == '__main__':
	try:
		if len(sys.argv[1]) > 0: # verifica se o topico foi passado como paramentro ao executar o codigo
			client = mqtt.Client()
			client.connect("192.168.25.63") # conexao com a maquina que a porta 1883 esta aberta
			client.subscribe(sys.argv[1])
			client.on_message = on_message
			client.loop_forever()
	except Exception as e:
		print ('\nErro: Informe o topico como proximo parametro\n')
