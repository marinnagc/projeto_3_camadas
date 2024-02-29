#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading
# tentando usar o getstatus antes do get ser usado, precisa controlar o tempo
# como o thread roda de maneira separada a gnt precisa esperar ele ser false pra gnt ler
# o sendData ja tem o buffer ligado?
# queremos usar o get status so quando o thread for desligado pq ai teremos ctz q todos os dados foram enviados para isso
# para isso podemos usar a variavel mutex???
# AAAAAAAAAA N SEI

# Class
class RX(object):
  
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.threadStop  = False
        self.threadMutex = True
        self.READLEN     = 1024

    def thread(self): 
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN)
                if (nRx > 0):
                    self.buffer += rxTemp  
                time.sleep(0.01)

    def threadStart(self):       
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def getIsEmpty(self):
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    # tamanho do buffer
    def getBufferLen(self):
        return(len(self.buffer))

    # Essa função é útil quando você deseja obter todos os dados presentes no buffer em um determinado 
    # momento, garantindo que nenhum dado novo seja adicionado enquanto você está processando os 
    # dados existentes. A pausa e retomada da thread são utilizadas para evitar condições de corrida 
    # durante a manipulação do buffer.
    def getAllBuffer(self, len):
        self.threadPause() # Pausa a thread para evitar interferências durante a manipulação do buffer
        b = self.buffer[:] # Cria uma cópia do buffer
        self.clearBuffer() # Limpa o buffer, removendo todos os dados presentes.
        self.threadResume()# Retoma a execução da thread, permitindo que novos dados possam ser adicionados ao buffer.
        return(b)          # Retorna a cópia dos dados originais presentes no buffer

    # nData é número de bytes que você deseja obter do início do buffer de recepção
    # então ele retornará os primeiros nData bytes do Buffer


    # Essa função é útil quando você deseja obter uma quantidade específica 
    # de dados do início do buffer. Ela permite que você extraia dados do buffer de recepção,
    # processando-os ou enviando-os para outros componentes do sistema. 
    def getBuffer(self, nData):
        self.threadPause()                 # Pausa a thread para evitar interferências durante a manipulação do buffer
        b           = self.buffer[0:nData] # Obtém os primeiros nData bytes do buffer
        self.buffer = self.buffer[nData:]  # Remove os nData primeiros bytes do buffer
        self.threadResume()                # Retoma a execução da thread
        return(b)                          # Retorna os primeiros nData bytes do buffer


    # getNData é útil quando você precisa garantir que uma quantidade mínima de dados esteja disponível no buffer antes de prosseguir com o processamento desses dados
    # Este é um loop que continua enquanto o tamanho atual do buffer (self.getBufferLen()) for menor que o tamanho desejado (size)
    # Essencialmente, aguarda até que haja pelo menos size bytes no buffer.
    def getNData(self, size):
        while(self.getBufferLen() < size):
            time.sleep(0.05)    # A função dorme por 50 milissegundos antes de verificar novamente.              
        return(self.getBuffer(size))    # Quando o tamanho desejado de dados estiver disponível no buffer, a função chama self.getBuffer(size) para obter
                                        # exatamente a quantidade desejada de bytes do buffer e, em seguida, retorna esses dados.


    def clearBuffer(self):
        self.buffer = b""


