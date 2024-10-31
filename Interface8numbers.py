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
        self.tabuleiro = []  

        # Chama o menu inicial
        self.menu_inicial()

    def menu_inicial(self):
        """Menu inicial com as opções de jogo."""
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Escolha o modo de jogo:", font=("Arial", 14))
        label.pack(pady=20)

        btn_definirTabuleiro = tk.Button(self.root, text="Definir Tabuleiro", command=self.definir_tabuleiro)
        btn_definirTabuleiro.pack(pady=10)

        btn_jogar = tk.Button(self.root, text="Jogar Manualmente", command=self.iniciar_jogo_jogador)
        btn_jogar.pack(pady=10)

        btn_largura = tk.Button(self.root, text="Agente Inteligente (Busca em Largura)", command=lambda: self.iniciar_jogo_agente('largura'))
        btn_largura.pack(pady=10)

        btn_profundidade = tk.Button(self.root, text="Agente Inteligente (Busca em Profundidade)", command=lambda: self.iniciar_jogo_agente('profundidade'))
        btn_profundidade.pack(pady=10)

        btn_estrela = tk.Button(self.root, text="Agente Inteligente (Busca Heuristica Gulosa)", command=lambda: self.iniciar_jogo_agente('gulosa'))
        btn_estrela.pack(pady=10)

        btn_estrela = tk.Button(self.root, text="Agente Inteligente (Busca A*)", command=lambda: self.iniciar_jogo_agente('a_estrela'))
        btn_estrela.pack(pady=10)

        btn_relatorio = tk.Button(self.root, text="Gerar Relatório", command=self.gerar_relatorio)
        btn_relatorio.pack(pady=10) 

    def retorna_estado_inicial(self):
        """Retorna o estado inicial do tabuleiro."""
        self.tabuleiro = self.tabuleiro_inicial[:]
        self.atualizar_botoes() 
        self.menu_inicial()   

    def definir_tabuleiro(self):
        """Permite o usuário definir o tabuleiro manualmente."""
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Digite os números do tabuleiro (0 a 8, sendo 0 o espaço vazio):", font=("Arial", 14))
        label.pack(pady=20)

        self.entradas = []
        
        for i in range(3):
            frame = tk.Frame(self.root)
            frame.pack()
            for j in range(3):
                entrada = tk.Entry(frame, width=5, font=("Arial", 12))
                entrada.grid(row=i, column=j, padx=5, pady=5)
                self.entradas.append(entrada)

        btn_confirmar = tk.Button(self.root, text="Confirmar", command=self.confirmar_tabuleiro)
        btn_confirmar.pack(pady=10)

        btn_voltar = tk.Button(self.root, text="Voltar ao Menu", command=self.menu_inicial)
        btn_voltar.pack(pady=10)

        

    def confirmar_tabuleiro(self):
        """Confirma o tabuleiro definido manualmente pelo usuário."""
        tabuleiro = []
        for entrada in self.entradas:
            try:
                numero = int(entrada.get())
                if numero < 0 or numero > 8:
                    raise ValueError
                if numero == 0:
                    numero = ''
                tabuleiro.append(numero)
            except ValueError:
                tk.Message(self.root, text="Digite apenas números de 0 a 8.", font=("Arial", 12)).pack(pady=10)
                return
        
        if self.eh_resolvivel(tabuleiro):
            self.tabuleiro = tabuleiro
            self.tabuleiro_inicial = self.tabuleiro[:]  # Guarda o estado inicial pro replay

        self.menu_inicial()

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
        elif self.modo_jogo == 'gulosa':
            self.tempo_execucao[self.modo_jogo] = self.registrar_tempo(self.busca_gulosa)

    def registrar_tempo(self, func):
        """Mede o tempo de execução de uma busca."""
        inicio = time.time()
        func()
        fim = time.time()
        return fim - inicio

    def iniciar_jogo(self):
        """Prepara o tabuleiro e a interface pro jogo começar."""
        self.movimentos = 0
        if self.tabuleiro == []:
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
        """Busca em Profundidade para resolver o jogo."""
        profundidade_maxima = 20  # Limite para evitar loops infinitos

        def profundidade_limitada(estado_atual, caminho, profundidade):
            """Explora até uma profundidade máxima."""
            # Verifica se atingiu o estado de vitória
            if estado_atual == self.sequencia_vitoria:
                self.caminho_solucao = caminho
                self.executar_caminho(caminho)
                return True

            # Limite de profundidade para evitar loops infinitos
            if profundidade >= profundidade_maxima:
                return False

            # Marca o estado atual como visitado
            visitados.add(tuple(estado_atual))
            index_vazio = estado_atual.index('')

            # Explora movimentos possíveis a partir do estado atual
            for movimento in self.movimentos_permitidos(index_vazio):
                novo_estado = estado_atual[:]
                novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]

                # Chama a função recursiva se o novo estado ainda não foi visitado
                if tuple(novo_estado) not in visitados:
                    if profundidade_limitada(novo_estado, caminho + [movimento], profundidade + 1):
                        return True

            # Remove o estado atual dos visitados ao retroceder
            visitados.remove(tuple(estado_atual))
            return False

        # Inicializa o conjunto de estados visitados e executa a busca
        visitados = set()
        profundidade_limitada(self.tabuleiro, [], 0)

    
    def busca_a_estrela(self):
        """Busca A* para resolver o jogo."""
        def h(estado):
            """Função heurística: número de peças fora do lugar."""
            return sum(1 for i, j in zip(estado, self.sequencia_vitoria) if i != j and i != 0)

        # Substitui '' por 0 temporariamente para facilitar a comparação
        tabuleiro_numerico = [0 if x == '' else x for x in self.tabuleiro]
        sequencia_vitoria_numerica = [0 if x == '' else x for x in self.sequencia_vitoria]

        # Converte o estado inicial para tupla e adiciona à fila
        fila = [(h(tabuleiro_numerico), 0, tabuleiro_numerico, [])]
        visitados = set()

        while fila:
            _, custo, estado_atual, caminho = heapq.heappop(fila)
            
            if estado_atual == sequencia_vitoria_numerica:
                self.caminho_solucao = caminho
                # Restaura o tabuleiro para exibir '' no lugar do 0
                self.executar_caminho([movimento for movimento in caminho])
                return

            # Converte o estado atual para tupla para evitar duplicatas
            estado_tupla = tuple(estado_atual)
            if estado_tupla not in visitados:
                visitados.add(estado_tupla)
                index_vazio = estado_atual.index(0)  # Usa 0 para o vazio
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    novo_custo = custo + 1
                    heapq.heappush(fila, (novo_custo + h(novo_estado), novo_custo, novo_estado, caminho + [movimento]))

    def busca_gulosa(self):
        """Busca Gulosa para resolver o jogo."""
        def h(estado):
            """Função heurística: número de peças fora do lugar."""
            return sum(1 for i, j in zip(estado, self.sequencia_vitoria) if i != j and i != 0)

        # Substitui '' por 0 temporariamente no tabuleiro para facilitar a comparação
        tabuleiro_numerico = [0 if x == '' else x for x in self.tabuleiro]
        sequencia_vitoria_numerica = [0 if x == '' else x for x in self.sequencia_vitoria]

        # Inicializa a fila de prioridade com o tabuleiro convertido
        fila = [(h(tabuleiro_numerico), tabuleiro_numerico, [])]
        visitados = set()

        while fila:
            _, estado_atual, caminho = heapq.heappop(fila)

            # Verifica se o estado atual é o estado de vitória
            if estado_atual == sequencia_vitoria_numerica:
                self.caminho_solucao = caminho
                # Restaura a interface do tabuleiro para exibir '' ao invés de 0
                self.executar_caminho(caminho)
                return

            # Adiciona o estado atual aos visitados
            estado_tupla = tuple(estado_atual)
            if estado_tupla not in visitados:
                visitados.add(estado_tupla)
                index_vazio = estado_atual.index(0)  # Usa 0 para o espaço vazio
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    # Adiciona o novo estado à fila com sua heurística
                    heapq.heappush(fila, (h(novo_estado), novo_estado, caminho + [movimento]))


    def animacao_confetes(self):
        """Mostra uma animação de confetes na tela."""
        for botao in self.botoes:
            botao.config(bg="lightgreen")
        for _ in range(100):
            x = random.randint(0, 300)
            y = random.randint(0, 300)
            confete = tk.Label(self.root, text="🎉", font=("Arial", 20), fg="blue", bg="lightgreen")
            confete.place(x=x, y=y)
            self.root.update()
            self.root.after(100, confete.destroy)

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

        btn_replay = tk.Button(opcoes_frame, text="Repetir Caminho (Replay)", command=lambda: self.replay_caminho)
        btn_replay.pack(side="left", padx=5)

        btn_menu = tk.Button(opcoes_frame, text="Voltar ao Menu", command=self.retorna_estado_inicial)
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
