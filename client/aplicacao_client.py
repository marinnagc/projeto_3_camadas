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
                  

        imageR = "./img/llama1kb.jpg" #img a ser transmitida
        #carrega a img
        print("carregando imagem para transmissão: ")
        txBuffer = open(imageR,"rb").read() #imagem em bytes!


        def divide_pacotes(txBuffer):
            pacotes= []
            for i in range(len(txBuffer)):
                pacote = txBuffer[i:i + 140]
                pacotes.append(pacote)
            return pacotes, len(pacotes)


        def datagrama(tipo,n_pacotes,total_pacotes,dados):
            ceop = b'\xAA\xBB\xAA\xBB'
            if tipo == 1:
                head = b'\x01\xFF'+bytes(n_pacotes) + b'\x00\x00\x00\x00\x00\x00\x00'
                payload_1 = b''
                dtg = head+payload_1+ceop
            elif tipo == 3:
                head = b'\x03\xFF'+ bytes(n_pacotes) + bytes(total_pacotes) + b'\x00\x00\x00\x00\x00\x00'
                payload_1 = np.asarray(dados)
                dtg = head+payload_1+ceop
            elif tipo == 5:
                head = b'\x05\xFF'+ b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+payload_1+ceop
            return dtg

        com1.sendData()



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
