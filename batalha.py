import socket, pickle
from random import *

# Define tamanho do mapa, limpa pontuações, define caracteres.
porta1 = 62021
porta2 = 62022
tamanho_mapa = 10
vazio = " "
alvo = "0"
sub_num = 3
sub_amigo = "x"
sub_naufragado = "."
sub_tamanho = 1
navio_num = 3
navio_amigo = "X"
navio_naufragado = "+"
navio_tamanho = 2

rodada = 0
pontuacao_amiga = 0
pontuacao_inimiga = 0

# Função que Sorteia a posição dos barcos.
def sorteia_barco(num_barcos, tamanho_barco, simb_barco, matriz_mapa):
    """ Função que Sorteia a posição dos barcos. """

    while(num_barcos > 0):
        if(tamanho_barco == 1):
            x = randint(0, tamanho_mapa - 1)
            y = randint(0, tamanho_mapa - 1)
            if(matriz_mapa[x][y] == alvo):
                matriz_mapa[x][y] = simb_barco
                num_barcos -= 1
        if(tamanho_barco == 2):
            z = randint(0, 1)
            if(z == 0):
                x = randint(0, tamanho_mapa - 2)
                y = randint(0, tamanho_mapa - 1)
                if(matriz_mapa[x][y] == alvo and matriz_mapa[x+1][y] == alvo):
                    matriz_mapa[x][y] = simb_barco
                    matriz_mapa[x+1][y] = simb_barco
                    num_barcos -= 1
            if(z == 1):
                x = randint(0, tamanho_mapa - 1)
                y = randint(0, tamanho_mapa - 2)
                y2 = y + 1
                if(matriz_mapa[x][y] == alvo and matriz_mapa[x][y+1] == alvo):
                    matriz_mapa[x][y] = simb_barco
                    matriz_mapa[x][y+1] = simb_barco
                    num_barcos -= 1

# Função que computa os ataques realizados.
def computa_ataque(ataque, ataque_resultado, matriz_mapa):
    if(ataque_resultado == 0):
        print("Acertou água.")
        matriz_mapa[ataque[1]][ataque[0]] = vazio
        return
    if(ataque_resultado == 1):
        print("Sub inimigo atingido!")
        matriz_mapa[ataque[1]][ataque[0]] = sub_amigo
        return
    if(ataque_resultado == 2):
        print("Navio inimigo atingido!")
        matriz_mapa[ataque[1]][ataque[0]] = navio_amigo
        return
    else:
        print("ERRO")

# Função que computa os ataques sofridos.
def reporta_ataque(ataque, matriz_mapa):
    if(matriz_mapa[ataque[1]][ataque[0]] == alvo):
        print("Errou!")
        matriz_mapa[ataque[1]][ataque[0]] = vazio
        return 0
    if(matriz_mapa[ataque[1]][ataque[0]] == sub_amigo):
        print("Submarino naufragado.")
        matriz_mapa[ataque[1]][ataque[0]] = sub_naufragado
        return 1
    if(matriz_mapa[ataque[1]][ataque[0]] == navio_amigo):
        print("Navio atingido.")
        matriz_mapa[ataque[1]][ataque[0]] = navio_naufragado
        return 2
    else:
        print("ERRO")

# Função que recebe as coordenadas de ataque, envia, recebe resultado, e atualiza o mapa inimigo.
def jogo_ativo():
    print("\nMapa Inimigo:")
    print_mapa(matriz_mapa_inimigo)
    ataque_input = input("\nDigite a coordenada de ataque (X Y): ")
    ataque_x, ataque_y = ataque_input.split(" ")
    ataque_x = ord(ataque_x) - 65
    ataque_y = int(ataque_y)
    ataque = ataque_x, ataque_y
    print("Atacando coordenada:", ataque, "...")
    msg = pickle.dumps(ataque)
    tcp.send(msg)
    msg = tcp.recv(1024)
    ataque_resultado = pickle.loads(msg)
    computa_ataque(ataque, ataque_resultado, matriz_mapa_inimigo)
    print("\nMapa Inimigo:")
    print_mapa(matriz_mapa_inimigo)
    return ataque_resultado

# Função que receber as coordenadas de ataque, enviar o resultado, e atualizar o mapa amigo.
def jogo_passivo():
    print("\nMapa Amigo:")
    print_mapa(matriz_mapa_amigo)
    print("\nAguardando ataque...")
    msg = tcp.recv(1024)
    ataque = pickle.loads(msg)
    print("Bombardeiro atingiu", ataque, "!")
    ataque_reportado = reporta_ataque(ataque, matriz_mapa_amigo)
    msg = pickle.dumps(ataque_reportado)
    tcp.send(msg)
    print("\nMapa Amigo:")
    print_mapa(matriz_mapa_amigo)
    return ataque_reportado

# Função que imprime o mapa.
def print_mapa(matriz_mapa):
    cabecalho = []
    cabecalho.append("/")
    for i in range(1, tamanho_mapa + 1):
        cabecalho.append(chr(i + 65 - 1))
    print(" ".join(cabecalho))
    linha = 0
    for row in matriz_mapa:
        print(linha, " ".join(row))
        linha += 1
    print("\n. / x = Sub | + / X = Navio")

# Selecionar modo entre jogador 1 ou 2. Jogador 1 começa.
jogador = 0
endereco_jogador1 = "127.0.0.1"
while(jogador != 1 and jogador != 2):
    jogador = int(input("Escolha:\n1) Jogador 1\n2) Jogador 2\n"))

# Estabelece conexão.
if(jogador == 1):
    porta_origem = porta1
    porta_destino = porta2
else:
    porta_origem = porta2
    porta_destino = porta1

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = ("", porta_origem)

if(jogador == 1):
    print("Conexão iniciada. Aguardando cliente...")
    tcp.bind(origem)
    tcp.listen(1)
    tcp, destino = tcp.accept()
    msg = ""
    while(msg.upper() != "INICIO_BATALHA_NAVAL"):
        msg = tcp.recv(1024)
        msg = msg.decode()
    print("Conexão estabelecida!")
    msg = "BATALHA_NAVAL_INICIADA"
    tcp.send(msg.encode())
else:
    endereco_jogador1 = input("Digite o endereço do jogador 1, por exemplo, 127.0.0.1:\n")
    destino = endereco_jogador1
    tcp.connect((destino, porta_destino))
    msg = "INICIO_BATALHA_NAVAL"
    tcp.send(msg.encode())
    while(msg.upper() != "BATALHA_NAVAL_INICIADA"):
        msg = tcp.recv(1024)
        msg = msg.decode()
    print("Conexão estabelecida!")

# Cria e inicializa o mapa.
matriz_mapa_amigo = []
matriz_mapa_inimigo = []

for i in range(tamanho_mapa):
    matriz_mapa_amigo.append([alvo] * tamanho_mapa)
    matriz_mapa_inimigo.append([alvo] * tamanho_mapa)

# Sorteia os barcos.
sorteia_barco(navio_num, navio_tamanho, navio_amigo, matriz_mapa_amigo)
sorteia_barco(sub_num, sub_tamanho, sub_amigo, matriz_mapa_amigo)

pontuacao_maxima = ((sub_num * 1) + (navio_num * 2))

# Inicia o jogo.
print("Jogo iniciado. Jogador 1 começa.")

if(jogador == 1):
    print("\nMapa Amigo:")
    print_mapa(matriz_mapa_amigo)

if(jogador == 2):
    if(jogo_passivo() != 0):
        pontuacao_inimiga += 1
    rodada += 1

while(pontuacao_amiga <= pontuacao_maxima or pontuacao_inimiga <= pontuacao_maxima):
    if(jogo_ativo() != 0):
        pontuacao_amiga += 1
    if(jogo_passivo() != 0):
        pontuacao_inimiga += 1
    rodada += 1
    print("Rodada", rodada, "terminada. Pontuação amiga: ", pontuacao_amiga, "Pontuação inimiga: ", pontuacao_inimiga)
    if(pontuacao_amiga <= pontuacao_maxima):
        print("Parabéns, você ganhou!")
    if(pontuacao_inimiga <= pontuacao_maxima):
        print("Você perdeu. Melhor sorte na próxima vez.")

# Fecha a conexão.
tcp.close()