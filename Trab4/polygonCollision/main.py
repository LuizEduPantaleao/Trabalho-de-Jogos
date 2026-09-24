import pygame
import random
from shape import Polygon
from collision import Collide


pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quebra Bloco")
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsansms", 26)

# Cores para os itens
corfundo = (28, 28, 28)
corbloco = (0,255,127)
corblocofast = (255,165,0)
corblocoslow = (72,209,204)
corparabola = (154,205,50)
corraquete = (255, 250, 250)
corbola = (255, 80, 80)
cortext = (255, 255, 255)

pontos = 0
vidas = 3
estado = "jogando"
efecttime = 0
tipoefeito = None
multefect = 1
SUBPASSOS = 6 # Divisão do movimento da bola

# Criação da bola
bola = Polygon([(400, 300),(408, 304),(410, 312),(408, 320),
    (400, 324),(392, 320),(390, 312),(392, 304)])
velX = 4
velY = -4

# Criação da raquete
raquete = Polygon([(300, 540),(500, 540),(520, 555),
    (500, 570),(300, 570),(280, 555)])
velRaquete = 6

# Criação dos blocos de pontos, alguns com dos efeitos
def criarblocos():
    blocos = []
    for linha in range(3):
        for coluna in range(10):
            x = 60 + coluna * 70
            y = 60 + linha * 35
            bloco = Polygon([(x, y),(x + 60, y),(x + 60, y + 25),(x, y + 25)])
            blocos.append(bloco)

    # Escolhe aleatoriamente de 1 a 3 para cada blocos especiais para efeitos na quebra
    quantfast = random.randint(1, 3) 
    quantslow = random.randint(1, 3) 

    # Embaralha os blocos
    e = random.sample(blocos,quantfast + quantslow)
    blocoesp = {}

    # Blocos que dão efeito de rapidez
    for bloco in e[:quantfast]:
        blocoesp[id(bloco)] = "rapido"

    # Blocos que dão efeito de lentidão
    for bloco in e[quantfast:]:
        blocoesp[id(bloco)] = "lento"

    return blocos, blocoesp

blocos, blocoesp = criarblocos()

# Função de iniciar/avançar de rodada
def newrodada():
    global blocos, blocoesp
    global velX, velY
    blocos, blocoesp = criarblocos()

    # Reposiciona a bola
    bola.points = [(x + (400 - bola.bounding_box.centerx),
        y + (300 - bola.bounding_box.centery))for x, y in bola.points]
    bola.update_geometry()

    # Velocidade inicial da nova rodada
    velX = 4
    velY = -4

# Criação da parábola que fica na tela
pontosparabola = []

# Parte superior da parábola
for x in range(280, 521, 10):
    y = 350 + ((x - 400) ** 2) // 300
    pontosparabola.append((x, y))

# Parte inferior da faixa
for x in range(520, 279, -10):
    y = 360 + ((x - 400) ** 2) // 300
    pontosparabola.append((x, y))

parabola = Polygon(pontosparabola)


# Looping do jogo
running = True
while running:

    # Lista de eventos e comandos de teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Reinicio
            if event.key == pygame.K_r and estado != "jogando":
                estado = "jogando"
                vidas = 3
                pontos = 0
                efecttime = 0
                tipoefeito = None
                multefect = 1
                newrodada()

            if event.key == pygame.K_RETURN and estado == "vitoria":
                estado = "jogando"
                newrodada()

    if estado == "jogando":
       
        # Efeito temporário dos blocos especiais
        if efecttime > 0:
            efecttime -= 1 / 60
            if efecttime <= 0:
                velX /= multefect
                velY /= multefect
                efecttime = 0
                tipoefeito = None
                multefect = 1

        # Comando de movimento da raquete nas setas <- e -> ou A e D
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            raquete.points = [(x-velRaquete, y)for x, y in raquete.points]

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            raquete.points = [(x+velRaquete, y)for x, y in raquete.points]

        raquete.update_geometry()

        # Evita que a raquete saia da borda da tela horizontalmente
        if raquete.bounding_box.left < 0:
            deslocamento = -raquete.bounding_box.left

            raquete.points = [(x + deslocamento, y)for x, y in raquete.points]
            raquete.update_geometry()

        if raquete.bounding_box.right > WIDTH:
            deslocamento = WIDTH-raquete.bounding_box.right

            raquete.points = [(x + deslocamento, y)for x, y in raquete.points]
            raquete.update_geometry()

        # Movimentação da bola em subpassos
        for _ in range(SUBPASSOS):

            # Calculando o movimento de cada subpasso
            MovX = velX / SUBPASSOS
            MovY = velY / SUBPASSOS
            bola.points = [(x + MovX, y + MovY)for x, y in bola.points]
            bola.update_geometry()

            # Faz a bola colidir com a parede, invertendo a direção que estava seguindo
            if bola.bounding_box.left <= 0:
                velX = abs(velX)

            if bola.bounding_box.right >= WIDTH:
                velX = -abs(velX)

            if bola.bounding_box.top <= 0:
                velY = abs(velY)

            # Colisão com a raquete
            if Collide.polygon(bola, raquete):
                centrobola = bola.bounding_box.centerx
                centroraquete = raquete.bounding_box.centerx

                # Distância da bola em relação ao centro da raquete
                distancia = centrobola - centroraquete

                # Normaliza para aproximadamente -1 até 1
                limite = raquete.bounding_box.width / 2
                fator = distancia / limite

                # Impede que a bola fique completamente horizontal
                fator = max(-0.8, min(0.8, fator))
                vel = (velX ** 2 + velY ** 2) ** 0.5
                velX = fator * vel

                # Garante que a velocidade total continue igual
                velY = -(vel ** 2 - velX ** 2) ** 0.5

                # Tira a bola de dentro da raquete
                deslocamento = (raquete.bounding_box.top - bola.bounding_box.bottom)
                bola.points = [(x, y + deslocamento)for x, y in bola.points] # Movimenta a bola (ela é um poligno)
                bola.update_geometry()

            # Colisão com os blocos, calculando o lado para richocetear
            for bloco in blocos[:]:
                if Collide.polygon(bola, bloco):

                    # Armazena os delimitadores da caixa
                    Bolaret = bola.bounding_box
                    Blocoret = bloco.bounding_box

                    # Calcula quanto a bola entrou no bloco, verificando a direção 
                    # de menor sobreposição, assim definindo o local que a bola bateu
                    SobEsq = Bolaret.right - Blocoret.left
                    SobDir = Blocoret.right - Bolaret.left
                    SobUp = Bolaret.bottom - Blocoret.top
                    SobDown = Blocoret.bottom - Bolaret.top
                    MinSobreposicao = min(SobEsq, SobDir, SobUp, SobDown)

                    # Cada versão dessa vai definir qual direção a bola vai richochetear
                    # baseado no cálculo feito acima e nos ifs seguintes
                    if MinSobreposicao == SobEsq:
                        velX = -abs(velX)
                        deslocamento = (Blocoret.left - Bolaret.right)
                        bola.points = [(x + deslocamento, y)for x, y in bola.points]

                    elif MinSobreposicao == SobDir:
                        velX = abs(velX)
                        deslocamento = (Blocoret.right - Bolaret.left)
                        bola.points = [(x + deslocamento, y)for x, y in bola.points]

                    elif MinSobreposicao == SobUp:
                        velY = -abs(velY)
                        deslocamento = (Blocoret.top - Bolaret.bottom)
                        bola.points = [(x, y + deslocamento)for x, y in bola.points]

                    else:
                        velY = abs(velY)
                        deslocamento = (Blocoret.bottom - Bolaret.top)
                        bola.points = [(x, y + deslocamento)for x, y in bola.points]

                    bola.update_geometry()

                    # Pontuação
                    pontos += 1

                    # Verifica se o bloco possui efeito especial
                    if id(bloco) in blocoesp:

                        tipoefeito = blocoesp[id(bloco)]

                        # Se já havia outro efeito, desfaz o anterior
                        if multefect != 1:
                            velX /= multefect
                            velY /= multefect

                        if tipoefeito == "rapido":
                            multefect = 1.5

                        else:
                            multefect = 0.6

                        velX *= multefect
                        velY *= multefect

                        efecttime = 5

                    # Aceleração
                    velX *= 1.03
                    velY *= 1.03

                    # Remove o bloco
                    blocos.remove(bloco)

                    # Vitória
                    if len(blocos) == 0:
                        estado = "vitoria"

                    break

            # Colisão com a parábola
            if Collide.polygon(bola, parabola):

                # Posição aproximada da bola na parábola, onde colidiu
                x = bola.bounding_box.centerx

                # Inclinação da parábola naquele ponto que a bola atingiu
                inclinacao = (2 * (x - 400)) / 300

                # Vetor normal à superfície, utilizando para descobrir como a velocidade
                # deve ser refletida
                nx = -inclinacao
                ny = 1

                # Normaliza o vetor, calculando seu tamanho com Pitágoras 
                tamanho = (nx ** 2 + ny ** 2) ** 0.5
                nx /= tamanho
                ny /= tamanho

                # Velocidade atual guardada em um auxiliar
                auxvx = velX
                auxvy = velY

                # Reflexão da velocidade pela normal, definindo a sua direção
                # de acordo com a curvatura da parábola
                produto = auxvx * nx + auxvy * ny
                velX = auxvx - 2*produto * nx 
                velY = auxvy - 2*produto * ny

                # Afasta a bola da parábola
                bola.points = [(x - auxvx, y - auxvy)for x, y in bola.points]
                bola.update_geometry() # Todos estes update_geometry são para atualizar a geometria


     
        # Bola bate no chão, perdendo a vida ou morrendo
        if bola.bounding_box.bottom >= HEIGHT:
            vidas -= 1
            if vidas > 0:

                # Coloca a bola novamente um pouco acima do chão
                deslocamento = HEIGHT - bola.bounding_box.bottom - 2
                bola.points = [(x, y + deslocamento)for x, y in bola.points]
                bola.update_geometry()

                # Ricocheteia para cima
                velY = -abs(velY)

            else:
                estado = "game_over"

    # Desenho dos objetos
    screen.fill(corfundo)
    textopts = font.render(f"Pontos: {pontos}",True,(255, 255, 255))
    screen.blit(textopts, (10, 10))
    textovida = font.render(f"Vidas: {vidas}",True,(255, 255, 255))
    screen.blit(textovida, (680, 10))

    # Desenho bloco, verificando se ele é especial ou não
    for bloco in blocos:
        if id(bloco) in blocoesp:
            if blocoesp[id(bloco)] == "rapido":
                cor = corblocofast
            else:
                cor =corblocoslow

        else:
            cor = corbloco
        pygame.draw.polygon(screen,cor,bloco.points)

    pygame.draw.polygon(screen,corparabola,parabola.points)
    pygame.draw.polygon(screen,corraquete,raquete.points)

    # Efeito de cor na bola ao quebrar bloco especial
    if tipoefeito == "rapido":
        cor_bola = corblocofast

    elif tipoefeito == "lento":
        cor_bola = corblocoslow

    else:
        cor_bola = corbola

    pygame.draw.polygon(screen,cor_bola,bola.points)
    if estado == "vitoria":
        texto = font.render("PARABÉNS!", True, cortext)
        texto2 = font.render("ENTER: Avançar", True, cortext)
        texto3 = font.render("R: Reinicio", True, cortext)
        screen.blit(texto,texto.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        screen.blit(texto2,texto2.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(texto3,texto3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    elif estado == "game_over":
        texto = font.render("GAME OVER",True,cortext)
        instrucao = font.render("Pressione R para jogar novamente",True,cortext)
        screen.blit(texto,(WIDTH // 2-texto.get_width() // 2,230))
        screen.blit(instrucao,(WIDTH // 2-instrucao.get_width() // 2,280))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()