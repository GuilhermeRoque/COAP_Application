import socket
from messages import GET, POST, MessageType, MessageOptions, MessageTranslator, Response
from client import CoapClient
from projeto2_pb2 import Mensagem
from poller import Poller


UDP_IP = "localhost"
UDP_PORT = 5683
PATH = "ptc"

msg = Mensagem()
msg.placa = 'placa1'
msg.config.periodo = 1000
msg.config.sensores.extend(['sensor1', 'sensor2'])

'''
getMessage = GET(typeMessage=MessageType.CONFIRMABLE, token=4349, messageId=58374)
getMessage.setOption(MessageOptions.URI_HOST, UDP_IP)
getMessage.setOption(MessageOptions.URI_PORT, UDP_PORT)
getMessage.setOption(MessageOptions.URI_PATH, PATH)

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
'''


'''
cliente = CoapClient(UDP_IP, UDP_PORT, PATH)
#cliente.constroi(CoapClient.GET, CoapClient.CON)

# cliente = CoapClient(CoapClient.GET, CoapClient.NON, UDP_IP, UDP_PORT, PATH)

payload = msg.SerializeToString()
cliente.constroi(CoapClient.POST, CoapClient.CON, payload)
print("Payload ", payload)
# cliente = CoapClient(CoapClient.POST, CoapClient.NON, UDP_IP, UDP_PORT, PATH, payload=msg.SerializeToString())

poller = Poller()
poller.adiciona(cliente)
cliente.request()
poller.despache()

while not cliente.terminou:
    pass
print("Terminou")

resp = cliente._response

if resp is not None:
    print(resp.getPayload())
    print(resp.getCode())
    print(resp.getCodeClass())
    print(resp.getCodeDetail())
    code_resp = resp.getCodeClass() * 100 + resp.getCodeDetail()
    print(code_resp)
