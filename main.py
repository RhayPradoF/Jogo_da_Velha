import pygame
import sys
import random
from pygame.locals import *

# Inicialização
pygame.init()

# Constantes
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // 3
LINE_WIDTH = 15

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
GRAY = (200, 200, 200)

# Configuração da janela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jogo da Velha')
font = pygame.font.SysFont('Arial', 40)


class Jogo:
    def __init__(self):
        self.reset()
        self.dificuldade = "Fácil"
        self.estado = "MENU"  # MENU, JOGANDO, FIM
        self.vencedor = None
        self.historico = []  # Armazena os resultados das partidas (1: vitória do jogador, -1: derrota, 0: empate)
        self.perfect_play_prob = 0.8  # Probabilidade inicial de jogadas perfeitas no modo difícil

    def reset(self):
        self.grid = ["_"] * 9
        self.jogador = "X"
        self.game_over = False

    def atualizar_dificuldade(self):
        """Ajusta a dificuldade dinâmica baseada no histórico"""
        if len(self.historico) < 3:  # Espera pelo menos 3 partidas para ajustar
            return

        # Calcula a média das últimas 3 partidas
        media = sum(self.historico[-3:]) / 3

        # Ajusta a probabilidade de jogadas perfeitas
        if media < -0.5:  # Jogador perdendo muito
            self.perfect_play_prob = max(0.5, self.perfect_play_prob - 0.15)
        elif media > 0.5:  # Jogador ganhando muito
            self.perfect_play_prob = min(0.95, self.perfect_play_prob + 0.15)

        # Exibe no console (pode ser mostrado na tela também)
        print(f"Dificuldade ajustada: {self.perfect_play_prob * 100:.0f}% jogadas perfeitas")

    def desenhar_menu(self):
        screen.fill(WHITE)
        titulo = font.render("Jogo da Velha", True, BLACK)
        screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 100))

        # Botões de dificuldade
        pygame.draw.rect(screen, GREEN, (150, 200, 300, 60))
        facil = font.render("Fácil", True, WHITE)
        screen.blit(facil, (WIDTH // 2 - facil.get_width() // 2, 210))

        pygame.draw.rect(screen, GREEN, (150, 300, 300, 60))
        medio = font.render("Médio", True, WHITE)
        screen.blit(medio, (WIDTH // 2 - medio.get_width() // 2, 310))

        pygame.draw.rect(screen, GREEN, (150, 400, 300, 60))
        dificil = font.render("Difícil", True, WHITE)
        screen.blit(dificil, (WIDTH // 2 - dificil.get_width() // 2, 410))

    def desenhar_jogo(self):
        screen.fill(WHITE)
        # Desenha grid
        for i in range(1, 3):
            pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), LINE_WIDTH)
            pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_WIDTH)

        # Desenha X e O
        for i in range(9):
            row, col = i // 3, i % 3
            center_x = col * CELL_SIZE + CELL_SIZE // 2
            center_y = row * CELL_SIZE + CELL_SIZE // 2

            if self.grid[i] == "X":
                pygame.draw.line(screen, BLUE, (center_x - 50, center_y - 50), (center_x + 50, center_y + 50), 10)
                pygame.draw.line(screen, BLUE, (center_x - 50, center_y + 50), (center_x + 50, center_y - 50), 10)
            elif self.grid[i] == "O":
                pygame.draw.circle(screen, RED, (center_x, center_y), 50, 10)

    def desenhar_fim(self):
        screen.fill(WHITE)
        if self.vencedor == "X":
            texto = font.render("Você ganhou!", True, BLACK)
        elif self.vencedor == "O":
            texto = font.render("Computador ganhou!", True, BLACK)
        else:
            texto = font.render("Empate!", True, BLACK)

        screen.blit(texto, (WIDTH // 2 - texto.get_width() // 2, 200))

        pygame.draw.rect(screen, GREEN, (150, 300, 300, 60))
        voltar = font.render("Voltar ao Menu", True, WHITE)
        screen.blit(voltar, (WIDTH // 2 - voltar.get_width() // 2, 310))

    def verificar_vencedor(self, jogador):
        # Linhas
        for i in range(0, 9, 3):
            if self.grid[i] == jogador and self.grid[i + 1] == jogador and self.grid[i + 2] == jogador:
                return True

        # Colunas
        for i in range(3):
            if self.grid[i] == jogador and self.grid[i + 3] == jogador and self.grid[i + 6] == jogador:
                return True

        # Diagonais
        if (self.grid[0] == jogador and self.grid[4] == jogador and self.grid[8] == jogador) or \
                (self.grid[2] == jogador and self.grid[4] == jogador and self.grid[6] == jogador):
            return True

        return False

    def verificar_empate(self):
        return "_" not in self.grid

    def jogada_computador(self):
        if self.dificuldade == "Fácil":
            return self.jogada_facil()
        elif self.dificuldade == "Médio":
            return self.jogada_medio()
        else:
            return self.jogada_dificil()

    def jogada_facil(self):
        vazias = [i for i, x in enumerate(self.grid) if x == "_"]
        return random.choice(vazias) if vazias else -1

    def jogada_medio(self):
        # Tenta ganhar
        for i in range(9):
            if self.grid[i] == "_":
                self.grid[i] = "O"
                if self.verificar_vencedor("O"):
                    return i
                self.grid[i] = "_"

        # Bloqueia jogador
        for i in range(9):
            if self.grid[i] == "_":
                self.grid[i] = "X"
                if self.verificar_vencedor("X"):
                    self.grid[i] = "_"
                    return i
                self.grid[i] = "_"

        return self.jogada_facil()

    def jogada_dificil(self):
        # Com certa probabilidade, faz uma jogada não perfeita
        if random.random() > self.perfect_play_prob:
            return self.jogada_medio()  # Faz jogada do nível médio

        # Implementação do Minimax para jogada perfeita
        melhor_score = -float('inf')
        melhor_jogada = -1

        for i in range(9):
            if self.grid[i] == "_":
                self.grid[i] = "O"
                score = self.minimax(False)
                self.grid[i] = "_"

                if score > melhor_score:
                    melhor_score = score
                    melhor_jogada = i

        return melhor_jogada if melhor_jogada != -1 else self.jogada_medio()

    def minimax(self, is_maximizing):
        if self.verificar_vencedor("O"):
            return 1
        if self.verificar_vencedor("X"):
            return -1
        if self.verificar_empate():
            return 0

        if is_maximizing:
            melhor_score = -float('inf')
            for i in range(9):
                if self.grid[i] == "_":
                    self.grid[i] = "O"
                    score = self.minimax(False)
                    self.grid[i] = "_"
                    melhor_score = max(score, melhor_score)
            return melhor_score
        else:
            melhor_score = float('inf')
            for i in range(9):
                if self.grid[i] == "_":
                    self.grid[i] = "X"
                    score = self.minimax(True)
                    self.grid[i] = "_"
                    melhor_score = min(score, melhor_score)
            return melhor_score


def main():
    jogo = Jogo()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if jogo.estado == "MENU":
                    # Verifica clique nos botões de dificuldade
                    if 150 <= pos[0] <= 450:
                        if 200 <= pos[1] <= 260:
                            jogo.dificuldade = "Fácil"
                            jogo.estado = "JOGANDO"
                        elif 300 <= pos[1] <= 360:
                            jogo.dificuldade = "Médio"
                            jogo.estado = "JOGANDO"
                        elif 400 <= pos[1] <= 460:
                            jogo.dificuldade = "Difícil"
                            jogo.estado = "JOGANDO"

                elif jogo.estado == "JOGANDO" and not jogo.game_over:
                    # Jogada do humano
                    if jogo.jogador == "X":
                        col = pos[0] // CELL_SIZE
                        row = pos[1] // CELL_SIZE
                        idx = row * 3 + col

                        if 0 <= idx < 9 and jogo.grid[idx] == "_":
                            jogo.grid[idx] = "X"

                            if jogo.verificar_vencedor("X"):
                                jogo.vencedor = "X"
                                jogo.game_over = True
                                jogo.historico.append(1)  # Vitória do jogador
                                jogo.atualizar_dificuldade()
                                jogo.estado = "FIM"
                            elif jogo.verificar_empate():
                                jogo.vencedor = None
                                jogo.game_over = True
                                jogo.historico.append(0)  # Empate
                                jogo.atualizar_dificuldade()
                                jogo.estado = "FIM"
                            else:
                                jogo.jogador = "O"

                                # Jogada do computador
                                pygame.time.delay(500)
                                idx = jogo.jogada_computador()
                                if idx != -1:
                                    jogo.grid[idx] = "O"

                                    if jogo.verificar_vencedor("O"):
                                        jogo.vencedor = "O"
                                        jogo.game_over = True
                                        jogo.historico.append(-1)  # Vitória do computador
                                        jogo.atualizar_dificuldade()
                                        jogo.estado = "FIM"
                                    elif jogo.verificar_empate():
                                        jogo.vencedor = None
                                        jogo.game_over = True
                                        jogo.historico.append(0)  # Empate
                                        jogo.atualizar_dificuldade()
                                        jogo.estado = "FIM"
                                    else:
                                        jogo.jogador = "X"

                elif jogo.estado == "FIM":
                    # Botão voltar ao menu
                    if 150 <= pos[0] <= 450 and 300 <= pos[1] <= 360:
                        jogo.reset()
                        jogo.estado = "MENU"

        # Desenha a tela atual
        if jogo.estado == "MENU":
            jogo.desenhar_menu()
        elif jogo.estado == "JOGANDO":
            jogo.desenhar_jogo()
        elif jogo.estado == "FIM":
            jogo.desenhar_fim()

        pygame.display.update()
        clock.tick(30)


if __name__ == "__main__":
    main()