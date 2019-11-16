import socket
from messages import GET, POST, MessageType, MessageOptions
from projeto2_pb2 import Mensagem

UDP_IP = "localhost"
UDP_PORT = 5683

getMessage = GET(typeMessage=MessageType.CONFIRMABLE, token=4349, messageId=58374)
getMessage.setOption(MessageOptions.URI_HOST, UDP_IP)
getMessage.setOption(MessageOptions.URI_PORT, UDP_PORT)
getMessage.setOption(MessageOptions.URI_PATH, "ptc")

msg = Mensagem()
msg.placa = 'placa1'
msg.config.periodo = 1000
msg.config.sensores.extend(['sensor1', 'sensor2'])
postMessage = POST(typeMessage=MessageType.CONFIRMABLE, token=4350, messageId=58375, payload=msg.SerializeToString())
postMessage.setOption(MessageOptions.URI_HOST, UDP_IP)
postMessage.setOption(MessageOptions.URI_PORT, UDP_PORT)
postMessage.setOption(MessageOptions.URI_PATH, "ptc")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(postMessage.getMessage(), (UDP_IP, UDP_PORT))