import socket
from messages import GET, POST, MessageType, MessageOptions, MessageTranslator, Response
from client import CoapClient
from projeto2_pb2 import Mensagem

UDP_IP = "localhost"
UDP_PORT = 5683
PATH = "ptc"

'''
getMessage = GET(typeMessage=MessageType.CONFIRMABLE, token=4349, messageId=58374)
getMessage.setOption(MessageOptions.URI_HOST, UDP_IP)
getMessage.setOption(MessageOptions.URI_PORT, UDP_PORT)
getMessage.setOption(MessageOptions.URI_PATH, PATH)

msg = Mensagem()
msg.placa = 'placa1'
msg.config.periodo = 1000
msg.config.sensores.extend(['sensor1', 'sensor2'])
postMessage = POST(typeMessage=MessageType.CONFIRMABLE, token=4350, messageId=58375, payload=msg.SerializeToString())
postMessage.setOption(MessageOptions.URI_HOST, UDP_IP)
postMessage.setOption(MessageOptions.URI_PORT, UDP_PORT)
postMessage.setOption(MessageOptions.URI_PATH, "ptc")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(getMessage.getMessage(), (UDP_IP, UDP_PORT))
s = sock.recvfrom(1024)

mt = MessageTranslator(s[0])
resp = mt.translateResp()
if resp is None:
    print("Não conseguiu interpretar a mensagem")
else:
    print(resp.getPayload())
'''

# self, requestType, messageType, ip, port, path, payload=None
cliente = CoapClient(CoapClient.GET, CoapClient.CON, UDP_IP, UDP_PORT, PATH)
resp = cliente.request()
if resp is not None:
    print(resp.getPayload())