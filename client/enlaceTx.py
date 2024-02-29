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

# Class
class TX(object):
 
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.transLen    = 0
        self.empty       = True
        self.threadMutex = False
        self.threadStop  = False


    def thread(self):
        while not self.threadStop:
            if(self.threadMutex):
                self.transLen    = self.fisica.write(self.buffer)
                self.threadMutex = False

    def threadStart(self):
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    
    # Essa função é geralmente chamada para preparar dados para envio. 
    # Ao chamar sendBuffer com os dados desejados, você sinaliza para a 
    # thread de envio que ela pode começar a transmitir esses dados pela camada física.
    def sendBuffer(self, data):
        self.transLen   = 0         # Inicializa a variável transLen, ele seria como se fosse um contador que vai guardar algumas informacoes que serão enviadas
                                    # ele é zerado quando o envio é feito
        self.buffer = data          # Atribui os dados recebidos ao Buffer
        self.threadMutex  = True    # Ativa o mutex da thread, indicando que os dados estão prontos para serem enviados

    def getBufferLen(self):
        return(len(self.buffer))

    def getStatus(self):
        if self.threadMutex:
            time.sleep(0.05)
        return(self.transLen)
        

    def getIsBussy(self):
        return(self.threadMutex)

