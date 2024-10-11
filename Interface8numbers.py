import tkinter as tk
import random
import time
import matplotlib.pyplot as plt
from collections import deque
import heapq  # Pra busca A*

class JogoDos8Numeros:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo dos 8 Números")
        self.movimentos = 0
        self.modo_jogo = None  # Pra saber se é jogador ou IA
        self.sequencia_vitoria = [1, 2, 3, 4, 5, 6, 7, 8, '']
        self.caminho_solucao = []  # Caminho da solução
        self.tabuleiro_inicial = []  # Guarda o estado inicial pro replay
        self.tempo_execucao = {}  # Guarda os tempos de cada busca

        # Chama o menu inicial
        self.menu_inicial()

    def menu_inicial(self):
        """Menu inicial com as opções de jogo."""
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Escolha o modo de jogo:", font=("Arial", 14))
        label.pack(pady=20)

        btn_jogar = tk.Button(self.root, text="Jogar Manualmente", command=self.iniciar_jogo_jogador)
        btn_jogar.pack(pady=10)

        btn_largura = tk.Button(self.root, text="Agente Inteligente (Busca em Largura)", command=lambda: self.iniciar_jogo_agente('largura'))
        btn_largura.pack(pady=10)

        btn_profundidade = tk.Button(self.root, text="Agente Inteligente (Busca em Profundidade)", command=lambda: self.iniciar_jogo_agente('profundidade'))
        btn_profundidade.pack(pady=10)

        btn_estrela = tk.Button(self.root, text="Agente Inteligente (Busca A*)", command=lambda: self.iniciar_jogo_agente('a_estrela'))
        btn_estrela.pack(pady=10)

        btn_relatorio = tk.Button(self.root, text="Gerar Relatório", command=self.gerar_relatorio)
        btn_relatorio.pack(pady=10)

    def iniciar_jogo_jogador(self):
        """Inicia o jogo no modo manual."""
        self.modo_jogo = 'jogador'
        self.iniciar_jogo()

    def iniciar_jogo_agente(self, tipo_busca):
        """Inicia o jogo no modo IA (Largura, Profundidade ou A*)."""
        self.modo_jogo = tipo_busca
        self.iniciar_jogo()

        if self.modo_jogo == 'largura':
            self.tempo_execucao[self.modo_jogo] = self.registrar_tempo(self.busca_em_largura)
        elif self.modo_jogo == 'profundidade':
            self.tempo_execucao[self.modo_jogo] = self.registrar_tempo(self.busca_em_profundidade)
        elif self.modo_jogo == 'a_estrela':
            self.tempo_execucao[self.modo_jogo] = self.registrar_tempo(self.busca_a_estrela)

    def registrar_tempo(self, func):
        """Mede o tempo de execução de uma busca."""
        inicio = time.time()
        func()
        fim = time.time()
        return fim - inicio

    def iniciar_jogo(self):
        """Prepara o tabuleiro e a interface pro jogo começar."""
        self.movimentos = 0
        self.tabuleiro = self.embaralhar_tabuleiro()
        self.tabuleiro_inicial = self.tabuleiro[:]  # Guarda o estado inicial pro replay
        self.caminho_solucao = []

        for widget in self.root.winfo_children():
            widget.destroy()

        self.botoes = []
        for i in range(9):
            botao = tk.Button(self.root, text=str(self.tabuleiro[i]), width=10, height=5, command=lambda i=i: self.mover(i) if self.modo_jogo == 'jogador' else None)
            botao.grid(row=i//3, column=i%3)
            self.botoes.append(botao)

        # Mostra a contagem de movimentos
        self.label_movimentos = tk.Label(self.root, text=f"Movimentos: {self.movimentos}", font=("Arial", 12))
        self.label_movimentos.grid(row=3, column=0, columnspan=3)

    def embaralhar_tabuleiro(self):
        """Embaralha o tabuleiro garantindo que seja resolvível."""
        while True:
            tabuleiro = [1, 2, 3, 4, 5, 6, 7, 8, '']
            random.shuffle(tabuleiro)
            if self.eh_resolvivel(tabuleiro):
                return tabuleiro

    def eh_resolvivel(self, tabuleiro):
        """Verifica se o tabuleiro pode ser resolvido."""
        inversoes = 0
        for i in range(8):  # Ignora o espaço vazio
            for j in range(i + 1, 9):
                if tabuleiro[i] != '' and tabuleiro[j] != '' and tabuleiro[i] > tabuleiro[j]:
                    inversoes += 1
        return inversoes % 2 == 0

    def atualizar_botoes(self):
        """Atualiza os textos dos botões e a contagem de movimentos."""
        for i in range(9):
            self.botoes[i].config(text=str(self.tabuleiro[i]) if self.tabuleiro[i] != '' else '')
        self.label_movimentos.config(text=f"Movimentos: {self.movimentos}")

    def mover(self, i):
        """Move o número pro espaço vazio, se puder."""
        index_vazio = self.tabuleiro.index('')
        movimentos_permitidos = {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }

        if index_vazio in movimentos_permitidos[i]:
            self.tabuleiro[index_vazio], self.tabuleiro[i] = self.tabuleiro[i], self.tabuleiro[index_vazio]
            self.movimentos += 1
            self.atualizar_botoes()
            if self.tabuleiro == self.sequencia_vitoria:
                self.vitoria()

    def busca_em_largura(self):
        """Busca em Largura pra resolver o jogo."""
        fila = deque([(self.tabuleiro, [])])
        visitados = set()

        while fila:
            estado_atual, caminho = fila.popleft()
            if estado_atual == self.sequencia_vitoria:
                self.caminho_solucao = caminho
                self.executar_caminho(caminho)
                return

            if tuple(estado_atual) not in visitados:
                visitados.add(tuple(estado_atual))
                index_vazio = estado_atual.index('')
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    fila.append((novo_estado, caminho + [movimento]))

    def busca_em_profundidade(self):
        """Busca em Profundidade pra resolver o jogo."""
        def profundidade_limitada(estado_atual, caminho, profundidade_maxima):
            """Explora até uma profundidade máxima."""
            if estado_atual == self.sequencia_vitoria:
                self.caminho_solucao = caminho
                self.executar_caminho(caminho)
                return True

            if len(caminho) >= profundidade_maxima:
                return False

            index_vazio = estado_atual.index('')
            for movimento in self.movimentos_permitidos(index_vazio):
                novo_estado = estado_atual[:]
                novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                if profundidade_limitada(novo_estado, caminho + [movimento], profundidade_maxima):
                    return True
            return False

        # Limita a profundidade pra evitar loop infinito
        profundidade_maxima = 20
        profundidade_limitada(self.tabuleiro, [], profundidade_maxima)

    def busca_a_estrela(self):
        """Busca A* pra resolver o jogo."""
        def heuristica(estado_atual):
            """Calcula a distância de Manhattan como heurística."""
            distancia = 0
            for i in range(9):
                if estado_atual[i] != '' and estado_atual[i] != self.sequencia_vitoria[i]:
                    valor = estado_atual[i]
                    pos_atual = (i // 3, i % 3)
                    pos_objetivo = ((valor - 1) // 3, (valor - 1) % 3)
                    distancia += abs(pos_atual[0] - pos_objetivo[0]) + abs(pos_atual[1] - pos_objetivo[1])
            return distancia

        prioridade = [(heuristica(self.tabuleiro), self.tabuleiro, [])]
        visitados = set()

        while prioridade:
            _, estado_atual, caminho = heapq.heappop(prioridade)
            if estado_atual == self.sequencia_vitoria:
                self.caminho_solucao = caminho
                self.executar_caminho(caminho)
                return

            if tuple(estado_atual) not in visitados:
                visitados.add(tuple(estado_atual))
                index_vazio = estado_atual.index('')
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    heapq.heappush(prioridade, (heuristica(novo_estado) + len(caminho) + 1, novo_estado, caminho + [movimento]))

    def movimentos_permitidos(self, index_vazio):
        """Retorna os movimentos permitidos pro vazio."""
        return {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }[index_vazio]

    def executar_caminho(self, caminho, replay=False):
        """Executa o caminho da busca. Se for replay, não conta movimentos."""
        self.movimentos_iniciais = self.movimentos  # Guarda a contagem inicial
        for movimento in caminho:
            self.mover(movimento)
            self.root.update()
            self.root.after(500)
        if replay:
            self.movimentos = self.movimentos_iniciais  # Mantém o número de movimentos no replay
        self.opcoes_pos_execucao()

    def opcoes_pos_execucao(self):
        """Mostra as opções depois que a busca termina."""
        opcoes_frame = tk.Frame(self.root)
        opcoes_frame.grid(row=4, column=0, columnspan=3, pady=10)

        btn_replay = tk.Button(opcoes_frame, text="Repetir Caminho (Replay)", command=lambda: self.replay_caminho())
        btn_replay.pack(side="left", padx=5)

        btn_novo_tabuleiro = tk.Button(opcoes_frame, text="Novo Tabuleiro", command=self.iniciar_jogo)
        btn_novo_tabuleiro.pack(side="left", padx=5)

        btn_menu = tk.Button(opcoes_frame, text="Voltar ao Menu", command=self.menu_inicial)
        btn_menu.pack(side="left", padx=5)

    def replay_caminho(self):
        """Refaz o caminho sem contar os movimentos."""
        self.tabuleiro = self.tabuleiro_inicial[:]  # Restaura o estado inicial
        self.atualizar_botoes()
        self.root.after(500, lambda: self.executar_caminho(self.caminho_solucao, replay=True))

    def vitoria(self):
        """Mostra a animação de vitória com confetes."""
        for botao in self.botoes:
            botao.config(bg="lightgreen")
        self.root.after(1000, self.animacao_confetes)

    def animacao_confetes(self):
        """Animação de confetes."""
        cores = ["red", "blue", "yellow", "green", "purple"]
        for i in range(9):
            self.botoes[i].config(bg=random.choice(cores))

        self.root.after(500, lambda: self.animacao_confetes() if self.movimentos < 20 else self.opcoes_pos_execucao())

    def gerar_relatorio(self):
        """Gera um relatório com gráficos dos tempos de execução."""
        if not self.tempo_execucao:
            tk.messagebox.showinfo("Relatório", "Nenhuma execução registrada. Execute pelo menos uma busca.")
            return
        
        # Gera o gráfico de tempos
        algoritmos = list(self.tempo_execucao.keys())
        tempos = list(self.tempo_execucao.values())

        plt.figure(figsize=(8, 6))
        plt.bar(algoritmos, tempos, color=['blue', 'green', 'red'])
        plt.xlabel('Algoritmos de Busca')
        plt.ylabel('Tempo de Execução (segundos)')
        plt.title('Comparação de Tempos de Execução dos Algoritmos')
        
        # Salva o gráfico como imagem
        plt.savefig('relatorio_buscas.png')
        plt.show()

        tk.messagebox.showinfo("Relatório", "Relatório gerado e salvo como 'relatorio_buscas.png'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoDos8Numeros(root)
    root.mainloop()
