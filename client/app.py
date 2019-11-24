#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import socket
import time
from layer import Layer
from client import CoapClient
from projeto2_pb2 import Mensagem, Sensor


class AEvent(object):
    FRAME = 1
    TIMEOUT = 2
    ACK = 3
    ERROR = 4

    def __init__(self, eventType, data=None):
        self.eventType = eventType
        self.data = data

class App(Layer):

    START = 0
    WaitConf = 1
    Active = 2
    WaitAck = 3

    def __init__(self, timeout=5, sensores=None, placa=socket.gethostname()):
        #Para o poller
        self.timeout = timeout
        self.base_timeout = self.timeout
        self.fd = None

        self.enable_timeout()

        #Placa
        self.placa = placa
        #Sensores da placa
        self.sensores = sensores
        #Periodo
        self.state = App.START

        self.buffer = []

    def send_conf(self):
        msg = Mensagem()
        msg.placa = self.placa
        msg.config.periodo = self.timeout
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
        ev = AEvent(AEvent.TIMEOUT)
        self.handle_fsm(ev)

    def handle_fsm(self, ev):

        eventType = ev.eventType

        if self.state == App.START:
            if eventType == AEvent.TIMEOUT:
                print("START")
                self.send_conf()
                self.state = App.WaitConf

        elif self.state == App.WaitConf:
            if eventType == AEvent.FRAME and (ev.data.getCodeDetail() == 4 or ev.data.getCodeDetail() == 1):
                msg = Mensagem()
                msg.ParseFromString(ev.data.getPayload())
                self.timeout = msg.config.periodo/1000
                print("PERIODO ATUALIZADO PARA: ", self.timeout)
                self.state = App.Active
            elif eventType == AEvent.ERROR:
                self.state = App.START
            else:
                self.state = App.Active

        elif self.state == App.Active:
            if eventType == AEvent.TIMEOUT:
                self.send_collected_data()
                self.state = App.WaitAck

        elif self.state == App.WaitAck:
            if eventType == AEvent.FRAME:
                if ev.data.getCodeDetail() == 4 or ev.data.getCodeDetail() == 1:
                    msg = Mensagem()
                    msg.ParseFromString(ev.data.getPayload())
                    self.timeout = msg.config.periodo/1000
                    print("PERIODO ATUALIZADO PARA: ", self.timeout)
                    self.state = App.Active
            elif eventType == AEvent.ACK:
                self.state = App.Active
            elif eventType == AEvent.ERROR:
                self.state = App.START

    def notify(self, data, *info):
        if data is not None:
            if data.getCodeClass() == 2:
                if data.getPayload() is not None:
                    ev = AEvent(AEvent.FRAME, data)
                    print("DATA")
                else:
                    ev = AEvent(AEvent.ACK)
                    print("ACK")
            else:
                ev = AEvent(AEvent.ERROR)
                print("ERRO")

        else:
            ev = AEvent(AEvent.ERROR)
            print("ERRO")

        self.handle_fsm(ev)
