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

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta


serialName = "COM5"                  # Windows(variacao de)

def divide_pacotes(txBuffer):
    pacotes= []
    for i in range(0,len(txBuffer),140):
        pacote = txBuffer[i:i + 140]
        if len(pacote) < 140:
            pacote += b'\x00' * (140 - len(pacote))
        pacotes.append(pacote)

    return pacotes, len(pacotes)

# num e o numero de pacote atual
# len(dados) e o tamanho do pacote
def datagrama(tipo, num, total_pacotes, dados, numero_img):
    ceop = b'\xAA\xBB\xAA\xBB'
    if tipo == 1: # chamado do cliente enviado ao servidor convidando-o para a transmissão
        head = b'\x01\xFF'+ (total_pacotes).to_bytes(1, 'big') + (numero_img).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop
    elif tipo == 3: # envio de pacotes (mostra x de y pacotes enviados)
        head = b'\x03'+ (num).to_bytes(1, 'big') + (total_pacotes).to_bytes(1, 'big') + (len(dados)).to_bytes(1, 'big')+ b'\x00\x00\x00\x00\x00\x00'
        payload_1 = dados
        dtg = head+payload_1+ceop
    elif tipo == 5: # mensagem de time out
        head = b'\x05\x00'+ b'\x00\x00\x00\x00\x00\x00\x00\x00'
        dtg = head+ceop

    return dtg

def escrever_log(mensagem, nome_arquivo="log.txt"):
    """
    Escreve uma mensagem de log com timestamp em um arquivo especificado.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(nome_arquivo, "a") as arquivo_log:
        arquivo_log.write(f"[{timestamp}] {mensagem}\n")

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")

        image1 = "./img/1.png" #img a ser transmitida
        image2 = "./img/2.png" 

        #carrega a img
        print("carregando imagem para transmissão: ")
        txBuffer1 = open(image1,"rb").read() #imagem em bytes!
        txBuffer2 = open(image2,"rb").read() #imagem em bytes!
        print("Imagem carregada")

        def envia_img(numero_img, img):
            com1.sendData(datagrama(1, 0, divide_pacotes(img)[1], 0, numero_img)) #envia o convite para o servidor (handshake)
            escrever_log(f"Convite enviado para o servidor.", "log_cliente.txt")
            h,_ = com1.getData(10) #pega o head do server pra ver se ele aceitou o convite
            ceop,_ =com1.getData(4) #pega o ceop
            if h[0] == 2:
                escrever_log(f"Tem-se início o envio do arquivo de extensâo {numero_img}", "log_cliente.txt")
                com1.sendData(datagrama(3,1,divide_pacotes(img)[1],divide_pacotes(img)[0][0], numero_img)) #envia o primeiro pacote
                escrever_log("Pacote 1 enviado.", "log_cliente.txt")
                print("Pacote 1 enviado.")
                timeout = 10
                tempo_inicial = time.time()
                tempo_duracao = 0
                i = 2
                while i <= (divide_pacotes(img)[1]):
                    print ("teste", i)
                    while com1.rx.getBufferLen() == 0:
                        time.sleep(0.02)
                        tempo_duracao = time.time() - tempo_inicial
                        if tempo_duracao >= timeout:
                            print(tempo_duracao)
                            escrever_log("Time out.", "log_cliente.txt")
                            print("Time out")
                            break
                            com1.disable()

                    head,_ = com1.getData(10) #pega o head
                    ceop,_ =com1.getData(4) #pega o ceop
                    print("head que server mandou pro client: ", head)

                    if head[0] == 5:
                        escrever_log("Time out.", "log_cliente.txt")
                        com1.disable()
                        break
                    elif head[0] == 6:
                        escrever_log(f"Número do pacote esperado incorreto. Enviando novamente o pacote requisitado", "log_cliente.txt")
                        com1.sendData(datagrama(3, head[1], divide_pacotes(img)[1], divide_pacotes(img)[0][head[1]-1], numero_img))

                    elif head[0] == 7:
                        escrever_log(f"Erro na transmissao do pacote {head[1]}. Reenviá-lo.", "log_cliente.txt")
                        com1.sendData(datagrama(3, head[1], divide_pacotes(img)[1], divide_pacotes(img)[0][head[1]], numero_img))

                    elif head[0] == 4:
                        tempo_inicial = 0
                        tempo_inicial = time.time()
                        if (i-1) == divide_pacotes(img)[1]:
                            print("teste")
                            com1.getData(10)
                            com1.getData(4)
                            print(f"ultimo head mandado pelo server: ", head)
                            escrever_log(f"Envio do arquivo de extensão {numero_img} finalizado.", "log_cliente.txt")   
                            numero_img += 1
                        else:
                            com1.sendData(datagrama(3, i, divide_pacotes(img)[1], divide_pacotes(img)[0][i-1], numero_img)) #envia o proximo pacote
                            print("Pacote ", i)
                            escrever_log(f"Pacote {i} enviado.", "log_cliente.txt")
                            i += 1

                if time.time() - tempo_inicial > timeout:
                    escrever_log("Time out.", "log_cliente.txt")
                    com1.sendData(datagrama(5, 0, 0, 0, 0))
                    com1.disable()
                    print("Tempo de envio dos arquivos: ", time.time() - tempo_inicial)


        envia_img(1, txBuffer1)
        envia_img(2, txBuffer2)
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
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()



# Se durante a transmissão os fios que conectam os arduinos forem desconectados e reconectados, a transmissão deve continuar após a reconexão. 