from enlace import *
import time
import numpy as np
import random


def main():
    try:

        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        serialName = "COM6"                  # Windows(variacao de)
        com1 = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        print("esperando o primeiro byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        print("oi")
        com1.rx.clearBuffer()
        time.sleep(.1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")

        #rx = RX(fisica)
        
        rxBuffer, nRx = com1.getData(1)
        print(rxBuffer)

        contador_comandos = 0
        while rxBuffer[0] != 5:
            rxBuffer, nRx = com1.getData(int.from_bytes(rxBuffer,"big"))
            contador_comandos+=1
            print(rxBuffer)
            rxBuffer, nRx = com1.getData(1)
    
        print("Número de comandos que foram recebidos: {}" .format(contador_comandos))
        com1.sendData(np.asarray(bytes(contador_comandos)))
        # Processar os dados recebidos

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
