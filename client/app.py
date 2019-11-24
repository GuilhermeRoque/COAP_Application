#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import time
from layer import Layer
from client import CoapClient
from projeto2_pb2 import Mensagem, Sensor


class AEvent(object):
    FRAME = 1
    TIMEOUT = 2
    ACK = 3
    ERROR = 4

    def __init__(self, eventType, msg=None):
        self.eventType = eventType
        self.msg = msg

class App(Layer):

    START = 0
    WaitConf = 1
    Active = 2
    WaitAck = 3

    def __init__(self, periodo=5, sensores=None, placa="placaApp"):
        #Para o poller
        self.timeout = periodo
        self.base_timeout = self.timeout
        self.fd = 0

        self.enable_timeout()
        self.enable()

        #Placa
        self.placa = placa
        #Sensores da placa
        self.sensores = sensores
        #Periodo
        self.periodo = periodo
        self.state = App.START

        self.buffer = []

    def send_conf(self):
        msg = Mensagem()
        msg.placa = self.placa
        msg.config.periodo = self.periodo
        msg.config.sensores.extend(self.sensores)

        payload = msg.SerializeToString()
        self._lower.send(payload, CoapClient.POST, CoapClient.CON)


    def send_collected_data(self):
        print("SENDING DATA")
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
        cmd = input()
        if cmd == 'get' and self.state == App.Active:
            self._lower.send(None, CoapClient.GET, CoapClient.CON)
            self.state = App.WaitAck

    def handle_timeout(self):
        ev = AEvent(AEvent.TIMEOUT)
        self.handle_fsm(ev)

    def handle_fsm(self, ev):

        eventType = ev.eventType

        if self.state == App.START:
            if eventType == AEvent.TIMEOUT:
                self.send_conf()
                self.state = App.WaitConf

        elif self.state == App.WaitConf:
            if eventType == AEvent.FRAME:
                self.periodo = ev.msg.config.periodo
                self.state = App.Active

        elif self.state == App.Active:
            if eventType == AEvent.TIMEOUT:
                self.send_collected_data()
                self.state = App.WaitAck

        elif self.state == App.WaitAck:
            if eventType == AEvent.FRAME:
                self.state = App.Active
                #configure timeout

    def notify(self, data, *info):
        if data.getCodeClass() == 2:
            if data.getPayload() is not None:
                msg = Mensagem()
                msg.ParseFromString(data.getPayload())
                ev = AEvent(AEvent.FRAME, msg)
            else:
                ev = AEvent(AEvent.ACK)
        else:
            ev = AEvent(AEvent.ERROR)

        self.handle_fsm(ev)
