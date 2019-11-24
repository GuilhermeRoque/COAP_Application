#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import time

from poller import Callback, Poller
from server import sensorapp_pb2


class metodosProto(Callback):
    def __init__(self):
        self.poller = Poller()
        #File descriptor
        self.fd = None
        self.base_timeout = 10
        self.disable_timeout()
        self.disable()
        #Placa
        self.placa = None
        #Sensores da placa
        self.sensores = None

    def start(self):
        mensagem = sensorapp_pb2.Mensagem()
        mensagem.placa = self.placa
        sensores = []
        for i in range(len(self.sensores)):
            s = sensorapp_pb2.Sensor()
            s.nome = self.sensores[i]
            s.valor = random.randint(0, 50)
            s.timestamp = int(time.time())  # horário do sistema
            sensores.append(s)
        mensagem.dados.amostras.extend(sensores)
        payload = mensagem.SerializeToString()
        print('Payload: ', payload)


    def config(self, periodo, placa, *sensores):
        self.placa = placa
        self.sensores = sensores
        self.periodo = periodo
        mensagem = sensorapp_pb2.Mensagem()
        mensagem.placa = placa
        mensagem.config.periodo = periodo
        mensagem.config.sensores.extend(sensores)
        dados = mensagem.SerializeToString()
        payload = dados
        print('Payload: ', payload)

    def handle_timeout(self):
        mensagem = sensorapp_pb2.Mensagem()
        mensagem.placa = self.placa
        sensores = []
        for j in range(len(self.sensores)):
            s = sensorapp_pb2.Sensor()
            s.nome = self.sensores[j]
            s.valor = random.randint(0,50)
            s.timestamp = int(time.time()) #horário do sistema
            sensores.append(s)
        mensagem.dados.amostras.extend(sensores)
        payload = mensagem.SerializeToString()
        print('Payload: ', payload)


inicio = metodosProto()
inicio.start()