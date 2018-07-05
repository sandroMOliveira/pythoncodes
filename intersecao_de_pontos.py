#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sqrt


def Intersecao_de_pontos(pontos_raios):
  P0 = complex(pontos_raios[0][3],pontos_raios[0][4])
  P1 = complex(pontos_raios[1][3],pontos_raios[1][4])
  r0 = pontos_raios[0][2]
  r1 = pontos_raios[1][2]
  if type(P0) != complex or type(P1) != complex:
    raise TypeError("P0 e P1 precisam ser numeros complexos")
  # d = distancia
  d = sqrt((P1.real - P0.real)**2 + (P1.imag - P0.imag)**2)
  
  # se a distancia é maior que a soma dos raios
  if d > (r0 + r1):
    return False
  elif d < abs(r0 - r1): # se a distancia é menor que a diferenca dos raios
    return True
  elif d == 0:
    return True
  else:
    a = (r0**2 - r1**2 + d**2) / (2 * d)
    b = d - a
    h = sqrt(r0**2 - a**2)
    P2 = P0 + a * (P1 - P0) / d

    i1x = P2.real + h * (P1.imag - P0.imag) / d
    i1y = P2.imag - h * (P1.real - P0.real) / d
    i2x = P2.real - h * (P1.imag - P0.imag) / d
    i2y = P2.imag + h * (P1.real - P0.real) / d

    i1 = None
    i2 = None
    
    if i1x > 0 and i1y > 0:
      i1 = complex(i1x, i1y)
    if i2x > 0 and i2y > 0:
      i2 = complex(i2x, i2y)
    if i1 is not None and i2 is not None:
      return [i1, i2]
    elif i1:
      return [i1]
    elif i2:
      return [i2]