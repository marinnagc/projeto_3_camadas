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

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)


def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1 = enlace(serialName)
        com1.enable()
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)
            
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
                  
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        commands = {
            1: [0x00, 0x00, 0x00, 0x00],
            2: [0x00, 0x00, 0xFF, 0x00],
            3: [0xFF, 0x00, 0x00],
            4: [0x00, 0xFF, 0x00],
            5: [0x00, 0x00, 0xFF],
            6: [0x00, 0xFF],
            7: [0xFF, 0x00],
            8: [0x00],
            9: [0xFF],
        }

        n_comandos = random.randint(10, 30)
        print("Número de comandos a serem enviados: {}" .format(n_comandos))
        lista_comandos = [random.randint(1, 9) for _ in range(n_comandos)]

        txBuffer = bytes() #aqui temos que transformar a lista de inteiros em bytes
        for co in lista_comandos:
            b = bytearray([len(commands[co])]+commands[co])
            print(b)
            txBuffer += b
            tamanho =list(b)[0]
            print("tamanho do comando: {}" .format(tamanho))
        txBuffer += bytes([5])
        
        com1.sendData(txBuffer)
        txLen = len(txBuffer)
        # rxBuffer, nRx = com1.getData(txLen)

        #ESCREVE ARQUIVO CÓPIA
        # print("Salvando dados no arquivo: ")
        # txBuffer.write(rxBuffer)
       
        # print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
            
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
        
        com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.

        print("Recepção de dados iniciada")
        # rxBuffer, nRx = com1.getData(1)
        timeout = 5
        rx = RX(fisica)
        tempo_inicial = time.time()
        tempo_duracao = 0
        while com1.rx.getBufferLen() < 1:
            #print(com1.rx.getBufferLen())
            tempo_fim = time.time()
            tempo_duracao = tempo_fim - tempo_inicial

            if tempo_fim - tempo_inicial > timeout:
                print("Time out!")
                com1.disable()
                break
            com1.rx.getBufferLen()

        rxBuffer, nRx = com1.getData(1)
        comandos_recebidos = int.from_bytes(rxBuffer, byteorder='big')
        print(comandos_recebidos)
        print("Tempo de duração da comunicação: {}" .format(tempo_duracao))

        if comandos_recebidos == n_comandos:
            print("recebeu {} comandos! A quantidade de comandos foi igual." .format(comandos_recebidos))
        else:
            print("Ops! recebeu {} comandos! A quantidade de comandos foi diferente do esperado." .format(comandos_recebidos))
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos
        #txLen = len(txBuffer)
        #rxBuffer, nRx = com1.getData(txLen)
        # print("recebeu {} bytes" .format(len(rxBuffer)))
        
        '''for i in range(len(rxBuffer)):
            print("recebeu {}" .format(rxBuffer[i]))'''
        

        '''txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))'''
    
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
