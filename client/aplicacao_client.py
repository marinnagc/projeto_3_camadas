import sys
from enlace import *
import time
import numpy as np
import random
import datetime
from crc import Calculator, Crc16, Crc8

serialName = "COM5"                  # Windows(variacao de)

def divide_pacotes(txBuffer):
    pacotes= []
    for i in range(0,len(txBuffer),140):
        pacote = txBuffer[i:i + 140]
        if len(pacote) < 140:
            pacote += b'\x00' * (140 - len(pacote))
        pacotes.append(pacote)

    return pacotes, len(pacotes)

def escrever_log(mensagem, nome_arquivo="log.txt"):
    """
    Escreve uma mensagem de log com timestamp em um arquivo especificado.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(nome_arquivo, "a") as arquivo_log:
        arquivo_log.write(f"[{timestamp}] {mensagem}\n")

def calculate_crc16(data):
    crc = 0xFFFF  # Valor inicial do CRC
    poly = 0x1021  # Polinômio CRC-16 (usando o polinômio comum para CRC-16)

    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF  # Garante que o CRC seja de 16 bits

    # Retorna os bytes do CRC em formato big-endian
    crc_bytes = crc.to_bytes(2, 'big')
    return crc_bytes

def main():
    try:
        calculator = Calculator(Crc8.CCITT)
        # num e o numero de pacote atual
        # len(dados) e o tamanho do pacote
        def datagrama(tipo, num, total_pacotes, dados, numero_img):
            ceop = b'\xAA\xBB\xAA\xBB'
            if tipo == 1: # chamado do cliente enviado ao servidor convidando-o para a transmissão
                head = b'\x01\xFF'+ (total_pacotes).to_bytes(1, 'big') + (numero_img).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            elif tipo == 3: # envio de pacotes (mostra x de y pacotes enviados)
                head = b'\x03'+ (num).to_bytes(1, 'big') + (total_pacotes).to_bytes(1, 'big') + (len(dados)).to_bytes(1, 'big')+ b'\x00\x00\x00\x00\x00' + calculator.checksum(dados).to_bytes(1, 'big')
                payload_1 = dados
                dtg = head+payload_1+ceop
            elif tipo == 5: # mensagem de time out
                head = b'\x05\x00'+ b'\x00\x00\x00\x00\x00\x00\x00\x00'
                dtg = head+ceop
            return dtg
        
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)

        print("Abriu a comunicação")
        image1 = "./img/1.png" #img a ser transmitida
        image2 = "./img/2.png" 

        #carrega a img
        print("carregando imagem para transmissão: ")
        txBuffer1 = open(image1,"rb").read() #imagem em bytes!
        txBuffer2 = open(image2,"rb").read() #imagem em bytes!
        print("Imagem carregada")

        numero_img = 1
        com1.sendData(datagrama(1, 0, divide_pacotes(txBuffer1)[1], 0, numero_img)) #envia o convite para o servidor (handshake)
        escrever_log(f"Convite enviado para o servidor.", "log_cliente.txt")
        h,_ = com1.getData(10) #pega o head do server pra ver se ele aceitou o convite
        print(h)
        ceop,_ =com1.getData(4) #pega o ceop
        ultimo = True
        if h[0] == 2: 
            print("Server aceitou o convite")
            while numero_img<=2:
                escrever_log(f"Tem-se início o envio do arquivo {numero_img}.png", "log_cliente.txt")
                com1.sendData(datagrama(3,1,divide_pacotes(txBuffer1)[1],divide_pacotes(txBuffer1)[0][0], numero_img)) #envia o primeiro pacote
                print("Pacote 1 enviado!")
                escrever_log(f"Pacote 1 enviado.", "log_cliente.txt")
                tempo_inicial = time.time()
                timeout = 10
                tempo_duracao = 0
                i = 1
                while i <= (divide_pacotes(txBuffer1)[1]):
                    while com1.rx.getBufferLen() < 14:
                        time.sleep(0.02)
                        tempo_duracao = time.time() - tempo_inicial
                        if tempo_duracao >= 1:
                            time.sleep(.5)
                            print("Reenviando confirmação de recebimento do pacote")
                            print(numero_img)
                            print(i)
                            com1.sendData(datagrama(3, i-1, divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][i-2], numero_img)) #envia o proximo pacote
                            tempo_inicial = time.time()

                    head,_ = com1.getData(10) #pega o head
                    ceop,_ =com1.getData(4) #pega o ceop
                    i = head[1]
                    print("head que server mandou pro client: ", head)

                    if head[0] == 5:
                        escrever_log("Time out.", "log_cliente.txt")
                        print("Time out")
                        break

                    elif head[0] == 6:
                        print(head[1])
                        escrever_log(f"Número do pacote esperado incorreto. Enviando novamente o pacote requisitado", "log_cliente.txt")
                        com1.sendData(datagrama(3, head[1], divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][head[1]-1], numero_img))
                        print("pacote a ser reenviado, tipo 6",datagrama(3, head[1], divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][head[1]-1], numero_img))

                    elif head[0] == 7:
                        escrever_log(f"Erro na transmissao do pacote {head[1]}. Reenviá-lo.", "log_cliente.txt")
                        com1.sendData(datagrama(3, head[1], divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][head[1]-1], numero_img))

                    elif head[0] == 4:
                        if head[1] == 255:
                            escrever_log(f"Envio do arquivo {numero_img}.png finalizado.", "log_cliente.txt")   
                            ultimo = True
                            com1.disable()
                            print("Comunicação encerrada")
                            sys.exit()

                        elif i == divide_pacotes(txBuffer1)[1] and ultimo:
                            print("contador é igual ao numero de pacotes") 
                            print("enviando o ultimo pacote")
                            com1.sendData(datagrama(3, head[1], divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][head[1]-1], numero_img)) #envia o proximo pacote
                            tempo_inicial=time.time()
                            ultimo = False
                            numero_img += 1

                        elif i != divide_pacotes(txBuffer1)[1]:
                            tempo_inicial = time.time()
                            com1.sendData(datagrama(3, head[1], divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][head[1]-1], numero_img)) #envia o proximo pacote
                            time.sleep(.5)
                            print("Pacote ", i)
                            print("pacote a ser enviado",datagrama(3, head[1], divide_pacotes(txBuffer1)[1], divide_pacotes(txBuffer1)[0][head[1]-1], numero_img))
                            escrever_log(f"Pacote {i} enviado.", "log_cliente.txt")

        print("Razão entre os tamanhos dos arquivos: ", len(txBuffer1)/len(txBuffer2))  
        
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable() 
        

if __name__ == "__main__":
    main()


