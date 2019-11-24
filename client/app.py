#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import time
from layer import Layer
from client import CoapClient
from projeto2_pb2 import Mensagem, Sensor
from client import CEvent

class App(Layer):

    START = 0
    WaitConf = 1
    Active = 2
    WaitAck = 3

    def __init__(self, periodo=5, sensores=None, placa="placaApp"):
        #Para o poller
        self.timeout = periodo
        self.base_timeout = self.timeout
        self.fd = None

        self.enable_timeout()

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
        pass

    def handle_timeout(self):
        print("TIMEOUT")
        ev = CEvent(CEvent.TIMEOUT)
        self.handle_fsm(ev)

    def handle_fsm(self, ev):

        eventType = ev.eventType

        if self.state == App.START:
            if eventType == CEvent.TIMEOUT:
                print("START")
                self.send_conf()
                self.state = App.WaitConf
        elif self.state == App.WaitConf:
            if eventType == CEvent.FRAME:
                print("CONF RCV")
                self.state = App.Active
        elif self.state == App.Active:
            if eventType == CEvent.TIMEOUT:
                print("SENDING DATA")
                self.send_collected_data()
                self.state = App.WaitAck
        elif self.state == App.WaitAck:
            if eventType == CEvent.FRAME:
                print("ACK RCV")
                self.state = App.Active

    def notify(self, data, *info):
        print("FRAME: ", data.getPayload())
        ev = CEvent(CEvent.FRAME, data)
        self.handle_fsm(ev)
