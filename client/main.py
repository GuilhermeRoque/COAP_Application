from poller import Poller
from app import App
from client import CoapClient

UDP_IP = "localhost"
UDP_PORT = 5683
PATH = "ptc"

if __name__ == '__main__':
    poller = Poller()
    app = App(placa="placaA", sensores=["sensorA", "sensorB"])
    coap = CoapClient(UDP_IP, UDP_PORT, PATH)

    app._lower = coap
    coap._upper = app

    poller.adiciona(app)
    poller.adiciona(coap)

    poller.despache()
