# COAP_Application

#### **Faça requisições para o servidor usando a URI /ptc.**

- Mensagens GET:
  Geram respostas contendo a listagem de placas de aquisição de dados conhecidas e respectivos sensores.

- Mensagens POST do tipo Config: 
  Podem ser usadas para a placa se registrar no servidor. 
  A resposta a esse tipo de mensagem é um payload também do tipo Config com o valor de período de anostragem a ser usado pela placa.

- Mensagens POST do tipo Dados: 
  São usadas para enviar os valores amostrados dos sensores. 
  O servidor de coleta recusa mensagens Dados de placas não registradas. Valores de sensores desconhecidos são ignorados. 
  
- Para executar pelo terminal vá para o diretório raiz do projeto e execute os comandos:
  1. **python3 server/sensorapp.py** (para o servidor)
  2. **python3 client/main.py** (para o cliente)

>Formato da mensagem COAP.
>
![](https://github.com/GuilhermeRoque/COAP_Application/blob/master/coapFormat.png)

>Máquina de estado.
>
![](https://github.com/GuilhermeRoque/COAP_Application/blob/master/fsm.png)

