#!/usr/bin/env python
# -*- coding: utf-8 -*-


def elevar(ponto):
  return pow(pow(ponto[0],2)+pow(ponto[1],2),.5)


def formatar(num):
  return float("{0:.5f}".format(num))


def triangulacao(pontos_raios):
  ponto1 = [pontos_raios[0][3],pontos_raios[0][4]]
  ponto2 = [pontos_raios[1][3],pontos_raios[1][4]]
  ponto3 = [pontos_raios[2][3],pontos_raios[2][4]]
  r1 = pontos_raios[0][2]
  r2 = pontos_raios[1][2]
  r3 = pontos_raios[2][2]

  # distancia do ponto 1 ao ponto 2
  # ( ((x1 - x2)^2)+((y1 - y2)^2) )^0.5
  p2p1Distancia = pow(pow(ponto2[0]-ponto1[0],2) + pow(ponto2[1] - ponto1[1],2),0.5);

  # o vetor unitário na direção x
  ex = [(ponto2[0]-ponto1[0]) / p2p1Distancia, (ponto2[1]-ponto1[1]) / p2p1Distancia]
  aux = [ponto3[0]-ponto1[0],ponto3[1]-ponto1[1]]
  # a magnitude assinada do componente x
  i = ex[0] * aux[0] + ex[1] * aux[1]

  # o vetor unitário na direção y
  aux2 = [ponto3[0]-ponto1[0]-i * ex[0], ponto3[1]-ponto1[1]-i * ex[1]]
  ey = [aux2[0] / elevar (aux2), aux2[1] / elevar (aux2)]
  # a magnitude assinada do componente y
  j = ey[0] * aux[0] + ey[1] * aux[1]

  # coordenadas
  x = (float(pow(r1,2)) - float(pow(r2,2)) + pow(p2p1Distancia,2)) / (2 * p2p1Distancia)
  y = (float(pow(r1,2)) - float(pow(r3,2)) + pow(i,2) + pow(j,2)) / (2 * j) - i * x / j

  finalX = ponto1[0]+ x * ex[0] + y * ey[0]
  finalY = ponto1[1]+ x * ex[1] + y * ey[1]
  return (formatar(finalX), formatar(finalY))