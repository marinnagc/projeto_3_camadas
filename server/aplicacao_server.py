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

        def datagrama(tipo,num,total_pacotes,num_ultimo_pacote):
            ceop = b'\xAA\xBB\xAA\xBB'
            if tipo == 2: # quero dados, pode me mandar
                head = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop


                # FALTA UMA MENSAGEM DE ERRO CASO EOP ESTEJA COM PROBLEMA OU PACOTE FORA DE ORDEM


            elif tipo == 4: # recebi dados corretos e printei o numero do ultimo pacote recebido
                head = b'\x04'+ bytes(num_ultimo_pacote) + b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 5: # mensagem de time out
                head = b'\x05\x00'+ b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 6: # numero correto de pacotes esperados ERRO
                head = b'\x06' + bytes(num_ultimo_pacote+1)+b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 7: # mensagens erro
                head = b'\x07' + bytes(num_ultimo_pacote) + b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop

            return dtg

        rxBuffer, nRx = com1.getData(4) #recebe a resposta do servidor
        while rxBuffer[0] != b'\x01':
            rxBuffer, nRx = com1.getData(4)
        com1.sendData(datagrama(2,0,0,0))
        
        timeout = 10
        rx = RX(fisica)
        tempo_inicial = time.time()
        tempo_duracao = 0
        while com1.rx.getBufferLen() < 1:
            #print(com1.rx.getBufferLen())
            tempo_fim = time.time()
            tempo_duracao = tempo_fim - tempo_inicial

            if tempo_fim - tempo_inicial > timeout:
                print("Time out! O server ficou mais de 10 segundos sem me mandar nenhum dado.")
                com1.sendData(datagrama(5, 0, 0, 0))
                com1.disable()
                break
            com1.rx.getBufferLen()
           
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.

        #txBuffer = imagem em bytes!
        txBuffer = datagrama  #isso é um array de bytes
       
        print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
            
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
               
        
        com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
          
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
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
