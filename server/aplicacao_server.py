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
import datetime
from crc import Calculator, Crc8
# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta


serialName = "COM9"                       # Windows(variacao de)

def datagrama(tipo, num_ultimo_pacote):
    ceop = b'\xAA\xBB\xAA\xBB'
    if tipo == 2: # quero dados, pode me mandar
        head = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop
    elif tipo == 4: # recebi dados corretos e printei o numero do ultimo pacote recebido
        head = b'\x04'+ (num_ultimo_pacote).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop
    elif tipo == 5: # mensagem de time out
        head = b'\x05\x00'+ b'\x00\x00\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop
    elif tipo == 6: # numero do pacote esperado incorreto
        head = b'\x06' + (num_ultimo_pacote).to_bytes(1, 'big')+b'\x00\x00\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop
    elif tipo == 7:  # ceop esta com problema ou pacote fora de ordem
        head = b'\x07' + (num_ultimo_pacote).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop
    return dtg

def salva_img(imagem, conteudo_img):
    nova_img = f'./img/{imagem}.png'
    f = open(nova_img, "wb")
    f.write(conteudo_img)
    f.close()
    return nova_img

def escrever_log(mensagem, nome_arquivo="log.txt"):
    """
    Escreve uma mensagem de log com timestamp em um arquivo especificado.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(nome_arquivo, "a") as arquivo_log:
        arquivo_log.write(f"[{timestamp}] {mensagem}\n")

def crc16(data):
    crc = 0x0000
    poly = 0x1021

    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF

    return crc
        
def main():
    try:
        calculator = Calculator(Crc8.CCITT)
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
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

        head, _ = com1.getData(10) #recebe o convite do client
        print(head[0],head[1])
        ceop, _ = com1.getData(4) #recebe o convite do client
        conteudo_img = bytearray()
        imagem = 1

        while imagem<=2:
            print("entrou")

            if head[0] == 1 and head[1] == 255:
                total_pacotes = head[2]
                
                #imagem = head[3]
                com1.sendData(datagrama(2, 0)) 
                print("tipo2")  # aceita o convite
            escrever_log(f"Comunicação iniciada com o client.", "log_server.txt")
            #print(cont)
            cont = 1
            print(cont)
            tempo_duracao=0
            timeout=10
            tempo_inicial = time.time()
            tempo_inicial2 = time.time()
            while cont <= total_pacotes:# and tempo_duracao< timeout:
                print("entrou no while",cont,'de',total_pacotes)
                print("head anterior",head[0],head[1])
                while com1.rx.getBufferLen() < 14:
                    time.sleep(0.02)
                    tempo_duracao = time.time() - tempo_inicial
                    tempo_duracao2 = time.time() - tempo_inicial2
                    if tempo_duracao >= 10:
                        print(tempo_duracao)
                        escrever_log(f"Time out. Não recebi o pacote", "log_server.txt")
                        print("Time out!")  
                        com1.sendData(datagrama(5,0))
                        com1.disable()
                        break
                    if tempo_duracao2 > 2:
                        print("reenviando confirmacao!")   
                        com1.sendData(datagrama(4,cont))
                        tempo_inicial2 = time.time() 

                head, _ = com1.getData(10)    
                crc_recebido = head[8]+head[9]
                print('novo head',head)
                payload,_ = com1.getData(head[3])
                #print('novo payload',payload)
                ceop,_ = com1.getData(4)
                print("novo ceop",ceop)
                #print("head2",head[0],head[1])
                #print(conteudo_img)
                if head[0] == 5:
                    escrever_log(f"Time out.", "log_server.txt")
                    com1.disable()
                elif head[0] == 3:
                    print("mensagem tipo 3")
                    CRC_ = calculator.checksum(payload)
                    escrever_log(f"Recebi uma mensagem tipo 3 (pacote)", "log_server.txt")
                    #tempo_fim = time.time()
                    #tempo_duracao = tempo_fim - tempo_inicial
                    if ceop != b'\xAA\xBB\xAA\xBB':
                        print("tipo 7 - erro de ceop")
                        com1.sendData(datagrama(7,head[1]))
                        com1.rx.clearBuffer()
                        escrever_log(f"7 - Pacote fora de ordem", "log_server.txt")
                    elif head[1] != cont or CRC_ != head[9]:
                        print("valor checksum")
                        print(CRC_)
                        print(head[9])
                        print(head[8])
                        print("tipo 6 - pacote errado",head[1],cont)
                        com1.sendData(datagrama(6,cont))
                        print(datagrama(6,cont),"k"*100)
                        escrever_log(f"6 - Pacote esperado era {cont} mas recebi {head[1]}", "log_server.txt")
                        #com1.rx.clearBuffer()
                    elif head[1] == cont and ceop == b'\xAA\xBB\xAA\xBB' and CRC_ == head[9]:#check_crc16(payload,crc_recebido):
                        print('tipo 4 - tudo certo')
                        escrever_log(f"Pacote veio correto!", "log_server.txt")
                        tempo_inicial = 0
                        tempo_inicial = time.time()
                        print('tipo 4')
                        #cont+=1
                        conteudo_img += payload
                        print(head[1])
                        if cont+1 == total_pacotes+1:
                            print("ultimo head",head)
                            if imagem == 1:
                                com1.sendData(datagrama(4,1)) # quero o primeiro pacote da segunda imagem
                            elif imagem ==2:
                                com1.sendData(datagrama(4,255))
                            salva_img(imagem,conteudo_img)
                            escrever_log(f"Recebeu o arquivo {imagem}.png", "log_server.txt")
                            conteudo_img = bytearray() # esvaziando a imagem
                            imagem +=1 # próxima imagem
                            if imagem == 3:
                                time.sleep(2)
                                com1.disable()
                                break
                            else:
                                cont = total_pacotes +1 # forçando o while a acabar
                                escrever_log(f"Iniciando envio do arquivo {imagem}.png", "log_server.txt")
                             
                            
                        else:
                            cont+=1
                            com1.sendData(datagrama(4,cont))
                            print("eu to pedindo",datagrama(4,cont))
                            escrever_log(f"Pedindo o próximo pacote {cont}", "log_server.txt")


 


        
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
# lado server. Para o envio de 2 arquivos, um total de 4 arquivos serão gerados. Dois em cada computador CHECK