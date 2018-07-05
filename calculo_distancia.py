#!/usr/bin/env python
# -*- coding: utf-8 -*-

def calculo_distancia(rssi, measured_power):
  if rssi == 0:
    return -1.0; # se nao eh possivel determinar a precisao, retorna -1.
  razao = float(rssi) / measured_power
  if razao < 1.0:
    return pow(razao, 10)
  else:
    # Os valores 0.89976, 7.7095 e 0.111
    # sao as 3 constantes calculadas quando é resolvido
    # a "best fit curve" dos dados medidos.
    precisao = (0.89976) * pow(razao, 7.7095) + 0.111
    return precisao