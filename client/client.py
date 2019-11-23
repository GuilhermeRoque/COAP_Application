import socket
from messages import GET, POST, MessageType, MessageOptions, MessageTranslator, Response, ResponseCode
import poller
import random
# import re

# TOKENS = []

class CoapTimeouts(object):
    ACK_TIMEOUT = 2
    ACK_RANDOM_FACTOR = 1.5
    MAX_RETRANSMIT = 4


class CEvent(object):
    FRAME = 1
    TIMEOUT = 2

    def __init__(self, eventType, frame=None):
        self.eventType = eventType
        self.frame = frame


class CoapClient(poller.Callback):
    START = 0
    WAIT_ACK = 1
    WAIT_CON = 2
    WAIT_NON = 3

    GET = 10
    POST = 11

    CON = 20
    NON = 21

    def __init__(self, requestType, messageType, ip, port, path, payload=None):
        self._requestType = requestType
        self._messageType = messageType
        self._ip = ip
        self._port = port
        self._path = path
        self._payload = payload
        self._retransmitions = 0
        self._poller = poller.Poller()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._state = CoapClient.START
        self._message = self._createMessage()
        self.enable()
        self.disable_timeout()
        self._response = None
        self.fd = self._sock
        self.base_timeout = random.randint(CoapTimeouts.ACK_TIMEOUT, CoapTimeouts.ACK_TIMEOUT * CoapTimeouts.ACK_RANDOM_FACTOR)
        self.timeout = self.base_timeout


    def _genToken(self):
        return random.randint(1, 65535)

    def _getMsgId(self):
        return random.randint(1, 65535)

    def _setUri(self, msg):
        # # URI Format: coap://localhost:5683/ptc
        # regex = re.compile("coap:\/\/(\S+):(\d+)\/(\w+)")
        # m = regex.match(self._uri)
        # host = m.group(1)
        # port = m.group(2)
        # path = m.group(3)
        msg.setOption(MessageOptions.URI_HOST, self._ip)
        msg.setOption(MessageOptions.URI_PORT, self._port)
        msg.setOption(MessageOptions.URI_PATH, self._path)


    def _createMessage(self):
        msg = None
        self._token = self._genToken()
        self._messageId = self._getMsgId()
        msgType = MessageType.CONFIRMABLE if self._messageType == CoapClient.CON else MessageType.NON_CONFIRMABLE
        if self._requestType == CoapClient.GET:
            msg = GET(typeMessage=msgType, token=self._token, messageId=self._messageId)
        else:
            msg = POST(typeMessage=msgType, token=self._token, messageId=self._messageId, payload=self._payload)

        self._setUri(msg)
        return msg

    def init(self):
        self._sock.sendto(self._message.getMessage(), (self._ip, self._port))
        if self._messageType == CoapClient.CON:
            self._state = CoapClient.WAIT_ACK
        else:
            self._state = CoapClient.WAIT_NON

    def _sendMessage(self):
        self._sock.sendto(self._message.getMessage(), (self._ip, self._port))
        self.enable_timeout()

    def _sendAck(self):
        ack = Response(typeMessage=MessageType.ACK, messageId=self._messageId, code=ResponseCode.EMPTY)
        self._sock.sendto(ack.getHeader(), (self._ip, self._port))

    def _end(self):
        self.disable_timeout()
        self.disable()

    def handle_fsm(self, event):
        # No estado waitAck, encaminhamos um pacote do tipo CON e agora aguardaremos o ACK
        # Neste caso pode vir um ACK ja com a resposta ou não. Caso não venha com a resposta,
        # ela virá num outro pacote CON
        if self._state == CoapClient.WAIT_ACK:
            # Reencaminha tres vezes. Se nao teve responsta, encerra.
            if event.eventType == CEvent.TIMEOUT:
                if self._retransmitions == CoapTimeouts.MAX_RETRANSMIT:
                    self.reload_timeout()
                    self._end()
                else:
                    self._retransmitions += 1
                    self._sendMessage()
                    self.base_timeout = self.base_timeout * 2   # PG.21 - Timeout doubles
                    self.reload_timeout()

            # Se nao for um evento de timeout, é um evento de frame, então tenta traduzir
            mt = MessageTranslator(event.frame)
            resp = mt.translateResp()

            # Se a resposta é None, é pq não conseguiu traduzir. Neste caso pode não ser um frame de resposta
            if resp is None:
                return

            msgId = resp.getMessageId()
            if msgId != self._messageId:
                # mensagem nao e pra mim
                return

            token = resp.getToken()
            if (token != self._token):
                # MsgId e igual, mas token nao. Parece que recebemos um ACK vazio
                # Ok, muda de estado, esperando um CON
                # Esta certo isso? Feito olhando a página 12 da RFC
                self._state = CoapClient.WAIT_CON
                self.reload_timeout()

            # Se passou, entao recebemos um ACK ja com a resposta
            self._response = resp
            self._end()

        # O estado WAIT_CON acontece quando enviamos um pacote do tipo CON e já recebemos um ACK,
        # porém ainda não recebemos a resposta. Sendo assim, neste estado, estamos justamente aguardando a resposta
        # e, se recebermos, devemos encaminhar um ACK
        elif self._state == CoapClient.WAIT_CON:
            if event.eventType == CEvent.TIMEOUT:
                # TODO o que fazer no caso de timeout?
                # Necessario olhar na norma o que fazer
                self._end()

            # Se nao for um evento de timeout, é um evento de frame, então tenta traduzir
            mt = MessageTranslator(event.frame)
            resp = mt.translateResp()

            if resp is None:
                return

            token = resp.getToken()
            if token != self._token:
                return

            self._response = resp
            self._end()

        # No estado WAIT_NON, enviamos uma requisição do tipo NON (nao confirmavel)
        # Entao só o que aguardamos é um pacote do tipo NON
        elif self._state == CoapClient.WAIT_NON:
            if event.eventType == CEvent.TIMEOUT:
                if self._retransmitions == CoapTimeouts.MAX_RETRANSMIT:
                    self.reload_timeout()
                    self._end()
                else:
                    self._retransmitions += 1
                    self._sendMessage()
                    self.base_timeout = self.base_timeout * 2   # PG.21 - Timeout doubles
                    self.reload_timeout()

            # Se nao for um evento de timeout, é um evento de frame, então tenta traduzir
            mt = MessageTranslator(event.frame)
            resp = mt.translateResp()

            # Se a resposta é None, é pq não conseguiu traduzir. Neste caso pode não ser um frame de resposta
            if resp is None:
                return

            token = resp.getToken()
            if (token != self._token):
                return

            # Resposta recebida
            self._response = resp
            self._end()


    def handle(self):
        ev = CEvent(CEvent.FRAME, self._sock.recvfrom(1024)[0])
        self.handle_fsm(ev)

    def handle_timeout(self):
        ev = CEvent(CEvent.TIMEOUT)
        self.handle_fsm(ev)

    def request(self):
        self._poller.adiciona(self)
        self._sendMessage()
        if self._messageType == CoapClient.CON:
            self._state = CoapClient.WAIT_ACK
        else:
            self._state = CoapClient.WAIT_NON

        self.enable_timeout()

        # O poller vai cuidar da maquina de estados olhando para o socket. Assim que finalizar (tendo resposta ou nao)
        # este metodo irá retornar e a resposta (objeto do tipo Reponse) sera entregue no return.
        self._poller.despache()
        return self._response

    def getResponse(self):
        return self._response