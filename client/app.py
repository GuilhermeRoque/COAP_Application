#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import time
from layer import Layer
from client import CoapClient
from projeto2_pb2 import Mensagem, Sensor
from client import CEvent

UDP_IP = "localhost"
UDP_PORT = 5683
PATH = "ptc"


class App(Layer):

    START = 0
    WaitConf = 1
    Active = 2
    WaitAck = 3

    def __init__(self, periodo=60, sensores=None, placa="placaApp", timeout=None):
        #Para o poller
        self.timeout = timeout
        #Placa
        self.placa = placa
        #Sensores da placa
        self.sensores = sensores
        #Periodo
        self.periodo = periodo
        self.state = App.START

    def send_conf(self):
        msg = Mensagem()
        msg.placa = self.placa
        msg.config.periodo = self.periodo
        msg.config.sensores.extend(self.sensores)

        payload = msg.SerializeToString()
        self._lower.send(payload, CoapClient.POST, CoapClient.CON)


    def send_collected_data(self):
        msg = Mensagem()
        msg.placa = self.placa
        sensores = []

        #build random data
        for i in range(len(self.sensores)):
            s = Sensor()
            s.nome = self.sensores[i]
            s.valor = random.randint(0, 50)
            s.timestamp = int(time.time())  # horário do sistema
            sensores.append(s)

        msg.dados.amostras.extend(sensores)
        payload = msg.SerializeToString()

        self._lower.send(payload, CoapClient.POST, CoapClient.CON)

    def handle(self):
        ev = CEvent(CEvent.FRAME, self._sock.recvfrom(1024)[0])
        self.handle_fsm(ev)

    def handle_timeout(self):
        ev = CEvent(CEvent.TIMEOUT)
        self.handle_fsm(ev)

    def handle_fsm(self, ev):
        if self.state == App.START:
            if ev == CEvent.TIMEOUT:
                self.send_conf()
                self.state = App.WaitConf
        elif self.state == App.WaitConf:
            if ev == CEvent.FRAME:
                self.state = App.Active
        elif self.state == App.Active:
            if ev == CEvent.TIMEOUT:
                self.send_collected_data()
                self.state = App.WaitAck
        elif self.state == App.WaitAck:
            if ev == CEvent.FRAME:
                self.state = App.Active