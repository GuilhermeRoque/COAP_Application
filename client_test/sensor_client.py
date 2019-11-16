import asyncio, time
from projeto2_pb2 import Mensagem, Sensor

from aiocoap import *


class SensorClient(object):

    def __init__(self):
        pass

    async def get(self):
        protocol = await Context.create_client_context()

        request = Message(code=GET, uri='coap://localhost:5683/ptc')
        # request = Message(code=GET, uri='coap://localhost:5683/.well-known/core')

        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result: %s\n%r'%(response.code, response.payload))


    async def postDados(self):
        protocol = await Context.create_client_context()

        # sensores = []
        # for i in range(1,3):
        #     sensor = Sensor()
        #     sensor.nome = 'sensor%d' % i
        #     sensor.valor = 3*i
        #     sensor.timestamp = int(time.time())

        msg = Mensagem()
        msg.placa = 'placa1'
        # msg.dados.amostras = sensores
        request = Message(code=POST, payload=msg.SerializeToString(), uri='coap://localhost:5683/ptc')

        try:
            response = await protocol.request(request).response
            resp = Mensagem()
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result: %s\n%r'%(response.code, response.payload))


    async def postConfig(self):
        protocol = await Context.create_client_context()

        msg = Mensagem()
        msg.config.periodo = 1000
        msg.placa = 'placa1'
        request = Message(code=POST, payload=msg.SerializeToString(), uri='coap://localhost:5683/ptc')

        try:
            response = await protocol.request(request).response
            resp = Mensagem()
            resp.ParseFromString(response.payload)
            print(resp.config.periodo)
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result: %s\n%r'%(response.code, response.payload))


def main():
    sensorClient = SensorClient()
    # asyncio.get_event_loop().run_until_complete(sensorClient.get())
    asyncio.get_event_loop().run_until_complete(sensorClient.postConfig())
    # asyncio.get_event_loop().run_until_complete(sensorClient.postDados())
    # asyncio.async(sensorClient.get())
    # asyncio.get_event_loop().run_forever()
    
    


if __name__ == "__main__":
    main()
