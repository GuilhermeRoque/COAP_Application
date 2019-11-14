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
  
- Para executar pelo terminal:
  Ir para o diretório raiz do projeto.
  Executar os comandos:
  1. source venv/bin/activate (se for criado um venv e isntalado os modulos em requirements.txt)
  2. python3.6 -m server.sensorapp (para o servidor)
  3. python3.6 -m client.coapGET (para o cliente)

![](https://github.com/GuilhermeRoque/COAP_Application/blob/master/coapFormat.png)

![](https://github.com/GuilhermeRoque/COAP_Application/blob/master/fsm.png)

