#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import random


# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta


serialName = "COM3"                  # Windows(variacao de)


def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")

        def datagrama(tipo, num_ultimo_pacote):
            ceop = b'\xAA\xBB\xAA\xBB'
            if tipo == 2: # quero dados, pode me mandar
                head = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 4: # recebi dados corretos e printei o numero do ultimo pacote recebido
                head = b'\x04'+ bytes(num_ultimo_pacote) + b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 5: # mensagem de time out
                head = b'\x05\x00'+ b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 6: # numero correto de pacotes esperados incorreto
                head = b'\x06' + bytes(num_ultimo_pacote+1)+b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 7: # mensagens erro
                head = b'\x07' + bytes(num_ultimo_pacote) + b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 8: # ceop esta com problema ou pacote fora de ordem
                head = b'\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            return dtg
        
        def salva_img(numero_img):
            numero_img = int.from_bytes(numero_img, "big")
            img = f'./img/{numero_img}.jpg'
            f = open(img, "wb")
            f.write(conteudo_img)
            f.close()

        head, _ = com1.getData(10) #recebe o convite do client
        if head[0] == 1 and head[1] == 255:
            total_pacotes_receb = head[1]
            numero_img = head[3]
            com1.sendData(datagrama(2, 0, 0, 0)) # aceita o convite

        h,_ = com1.getData(10) #pega o head do server pra ver se ele aceitou o convite 
            
        if h[0] == 3:
            timeout = 10
            rx = RX(fisica)
            tempo_inicial = time.time()
            tempo_duracao = 0
            while com1.rx.getBufferLen() < 1:
                tempo_fim = 0
                tempo_fim = time.time()
                tempo_inicial = 0
                tempo_inicial = time.time()
                tempo_duracao = 0
                tempo_duracao = tempo_fim - tempo_inicial
                com1.sendData(datagrama(3,1,0,0)) #envia o primeiro pacote 
                conteudo_img = bytearray()
                for i in range(1, total_pacotes_receb-1):
                    head,_ = com1.getData(10) #pega o head
                    payload,_ = com1.getData(head[3]) #pega o payload
                    ceop,_ =com1.getData(4) #pega o ceop
                    conteudo_img += payload
                    if head[0] == 5:
                        print("Time out!")
                        com1.disable()
                        break
                salva_img(numero_img)

                if tempo_fim - tempo_inicial > timeout:
                    print("Time out!")
                    com1.sendData(datagrama(5, 0, 0, 0))
                    com1.disable()
                    break
                com1.rx.getBufferLen()
                print("Tempo de envio: ", tempo_duracao)

        #txBuffer = imagem em bytes!
        txBuffer = datagrama  #isso é um array de bytes
       
        print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        
        com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
          
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
      
        #acesso aos bytes recebidos
        txLen = len(txBuffer)
        rxBuffer, nRx = com1.getData(txLen)
        print("recebeu {} bytes" .format(len(rxBuffer)))
        
        for i in range(len(rxBuffer)):
            print("recebeu {}" .format(rxBuffer[i]))
        
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()


# enviei uma foto, como faco p enviar outra CHECK
# computar/mostrar tempo CHECK
# razao entre tamanhos dos arquivos CHECK
# tirar os fios
# #Dois arquivos de log deve ser gerado durante a transmissão de cada arquivo. Um no client e outro no
# server. No arquivo deverá haver o registro de todas as intercorrências: pacote enviado com problema,
# time out. Deve haver também o horário e extensão do arquivo enviado no lado client e do recebido no
# lado server. Para o envio de 2 arquivos, um total de 4 arquivos serão gerados. Dois em cada computador
    