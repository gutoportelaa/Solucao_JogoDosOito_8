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
        self.modo_jogo = None  # Pra saber se é jogador IA
        self.sequencia_vitoria = [1, 2, 3, 4, 5, 6, 7, 8, '']
        self.caminho_solucao = []  # Caminho da solução
        self.tabuleiro_inicial = []  
        self.tempo_execucao = {}  # Guarda os tempos de cada busca
        self.tabuleiro = []  
        self.resultados = [[[],[],[],[],[]], [[],[],[],[],[]], [[],[],[],[],[]], [[],[],[],[],[]]]  # Guarda os resultados das buscas

        # Chama o menu inicial
        self.menu_inicial()

    def menu_inicial(self):
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

        self.tabuleiro = self.tabuleiro_inicial[:]
        self.atualizar_botoes() 
        self.menu_inicial()   

    def definir_tabuleiro(self):
        #Permite o usuário definir o tabuleiro manualmente.
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
        #Confirma o tabuleiro definido manualmente pelo usuário.
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
            self.tabuleiro_inicial = self.tabuleiro[:]  # guarda o estado inicial 

        self.menu_inicial()

    def iniciar_jogo_jogador(self):        #Inicia o jogo no modo manual.

        self.modo_jogo = 'jogador'
        self.iniciar_jogo()

    def iniciar_jogo_agente(self, tipo_busca):      #inicia o jogo no modo IA (Largura, Profundidade ou A*).
        
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

        inicio = time.time()
        func()
        fim = time.time()
        return fim - inicio

    def iniciar_jogo(self):

        self.movimentos = 0
        if self.tabuleiro.count('') != 1:
            self.tabuleiro = self.embaralhar_tabuleiro()
        self.tabuleiro_inicial = self.tabuleiro[:]  # guarda o estado inicial
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
        custo_de_tempo = 0 # quantidade de nos visitados
        custo_de_espaço = 0 # maior quantidade de espaços na fila
        nos_gerados = 0 # número total de nos gerados
        profundidade_busca = 0 # profundidade maxima da busca
        profundidade_solucao = 0 # profundidade da solucao

        """Busca em Largura pra resolver o jogo."""
        fila = deque([(self.tabuleiro, [])])
        visitados = set()

        while fila:
            estado_atual, caminho = fila.popleft()
            if estado_atual == self.sequencia_vitoria:
                profundidade_solucao = len(caminho)
                self.caminho_solucao = caminho
                self.resultados[0][0] = custo_de_tempo
                self.resultados[0][1] = custo_de_espaço
                self.resultados[0][2] = nos_gerados
                self.resultados[0][3] = profundidade_busca
                self.resultados[0][4] = profundidade_solucao
                self.executar_caminho(caminho)
                return

            nos_gerados+=1

            if tuple(estado_atual) not in visitados:
                visitados.add(tuple(estado_atual))
                custo_de_tempo += 1
                index_vazio = estado_atual.index('')
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    fila.append((novo_estado, caminho + [movimento]))

            if len(fila) > custo_de_espaço:
                custo_de_espaço = len(fila)

            profundidade_busca = len(caminho)


    def busca_em_profundidade(self):
        custo_de_tempo = 0
        custo_de_espaço = 0
        nos_gerados = 0
        profundidade_busca = 0
        profundidade_solucao = 0
        profundidade_maxima = 50  # Defina um limite razoável para a profundidade

        pilha = [(self.tabuleiro, [])]
        visitados = set()

        while pilha:
            estado_atual, caminho = pilha.pop()
            profundidade_atual = len(caminho)

            if profundidade_atual > profundidade_maxima:
                continue  # Ignora se ultrapassar o limite de profundidade

            if estado_atual == self.sequencia_vitoria:
                profundidade_solucao = profundidade_atual
                self.caminho_solucao = caminho
                self.resultados[1][0] = custo_de_tempo
                self.resultados[1][1] = custo_de_espaço
                self.resultados[1][2] = nos_gerados
                self.resultados[1][3] = profundidade_busca
                self.resultados[1][4] = profundidade_solucao
                self.executar_caminho(caminho)
                return

            nos_gerados += 1
            custo_de_tempo += 1
            visitados.add(tuple(estado_atual))

            index_vazio = estado_atual.index('')
            for movimento in reversed(self.movimentos_permitidos(index_vazio)):
                novo_estado = estado_atual[:]
                novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]

                if tuple(novo_estado) not in visitados:
                    pilha.append((novo_estado, caminho + [movimento]))

            custo_de_espaço = max(custo_de_espaço, len(pilha))
            profundidade_busca = max(profundidade_busca, profundidade_atual)

    
    def busca_a_estrela(self):

        custo_de_tempo = 0
        custo_de_espaço = 0
        nos_gerados = 0
        profundidade_busca = 0
        profundidade_solucao = 0


        def h(estado):           #Função heurística: número de peças fora do lugar.

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
                profundidade_solucao = len(caminho)
                self.caminho_solucao = caminho
                self.resultados[2][0] = custo_de_tempo
                self.resultados[2][1] = custo_de_espaço
                self.resultados[2][2] = nos_gerados
                self.resultados[2][3] = profundidade_busca
                self.resultados[2][4] = profundidade_solucao
                self.executar_caminho([movimento for movimento in caminho])
                return
            
            nos_gerados += 1

            # Converte o estado atual para tupla para evitar duplicatas
            estado_tupla = tuple(estado_atual)
            if estado_tupla not in visitados:
                visitados.add(estado_tupla)
                custo_de_tempo += 1
                index_vazio = estado_atual.index(0)  # Usa 0 para o vazio
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    novo_custo = custo + 1
                    heapq.heappush(fila, (novo_custo + h(novo_estado), novo_custo, novo_estado, caminho + [movimento]))

            custo_de_espaço = max(custo_de_espaço, len(fila))
            profundidade_busca = max(profundidade_busca, len(caminho))


    def busca_gulosa(self):

        custo_de_tempo = 0
        custo_de_espaço = 0
        nos_gerados = 0
        profundidade_busca = 0
        profundidade_solucao = 0

        def h(estado):
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
                profundidade_solucao = len(caminho)
                self.caminho_solucao = caminho
                # Restaura a interface do tabuleiro para exibir '' ao invés de 0
                self.resultados[3][0] = custo_de_tempo
                self.resultados[3][1] = custo_de_espaço
                self.resultados[3][2] = nos_gerados
                self.resultados[3][3] = profundidade_busca
                self.resultados[3][4] = profundidade_solucao
                self.executar_caminho(caminho)
                return

            nos_gerados += 1

            # Adiciona o estado atual aos visitados
            estado_tupla = tuple(estado_atual)
            if estado_tupla not in visitados:
                custo_de_tempo += 1
                visitados.add(estado_tupla)
                index_vazio = estado_atual.index(0)  # Usa 0 para o espaço vazio
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    # Adiciona o novo estado à fila com sua heurística
                    heapq.heappush(fila, (h(novo_estado), novo_estado, caminho + [movimento]))

            custo_de_espaço = max(custo_de_espaço, len(fila))
            profundidade_busca = max(profundidade_busca, len(caminho))


    def animacao_confetes(self):
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
        return {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }[index_vazio]

    def executar_caminho(self, caminho, replay=False):
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

        # mostrando os resultados segundo o tipo de busca escolhida
        if self.modo_jogo == 'largura':
            tk.Label(opcoes_frame, text=f"Tempo de Execução: {resultados[0]} nos visitados").pack()
            tk.Label(opcoes_frame, text=f"Custo de Tempo: {resultados[0]}").pack()
            tk.Label(opcoes_frame, text=f"Custo de Espaço: {resultados[1]}").pack()
            tk.Label(opcoes_frame, text=f"Nós Gerados: {resultados[2]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Busca: {resultados[3]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Solução: {resultados[4]}").pack()
        elif self.modo_jogo == 'profundidade':
            resultados = self.resultados[1]
            tk.Label(opcoes_frame, text=f"Tempo de Execução: {resultados[0]} nos visitados").pack()
            tk.Label(opcoes_frame, text=f"Custo de Tempo: {resultados[0]}").pack()
            tk.Label(opcoes_frame, text=f"Custo de Espaço: {resultados[1]}").pack()
            tk.Label(opcoes_frame, text=f"Nós Gerados: {resultados[2]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Busca: {resultados[3]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Solução: {resultados[4]}").pack()
        elif self.modo_jogo == 'a_estrela':
            resultados = self.resultados[2]
            tk.Label(opcoes_frame, text=f"Tempo de Execução: {resultados[0]} nos visitados").pack()
            tk.Label(opcoes_frame, text=f"Custo de Tempo: {resultados[0]}").pack()
            tk.Label(opcoes_frame, text=f"Custo de Espaço: {resultados[1]}").pack()
            tk.Label(opcoes_frame, text=f"Nós Gerados: {resultados[2]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Busca: {resultados[3]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Solução: {resultados[4]}").pack()
        elif self.modo_jogo == 'gulosa':
            resultados = self.resultados[3]
            tk.Label(opcoes_frame, text=f"Tempo de Execução: {resultados[0]} nos visitados").pack()
            tk.Label(opcoes_frame, text=f"Custo de Tempo: {resultados[0]}").pack()
            tk.Label(opcoes_frame, text=f"Custo de Espaço: {resultados[1]}").pack()
            tk.Label(opcoes_frame, text=f"Nós Gerados: {resultados[2]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Busca: {resultados[3]}").pack()
            tk.Label(opcoes_frame, text=f"Profundidade da Solução: {resultados[4]}").pack()
        
        btn_menu = tk.Button(opcoes_frame, text="Voltar ao Menu", command=self.retorna_estado_inicial)
        btn_menu.pack(side="left", padx=5)

    def replay_caminho(self):
        self.tabuleiro = self.tabuleiro_inicial[:]
        self.atualizar_botoes()
        self.root.after(500, lambda: self.executar_caminho(self.caminho_solucao, replay=True))

    def vitoria(self):
        for botao in self.botoes:
            botao.config(bg="lightgreen")
        self.root.after(1000, self.animacao_confetes)


    def gerar_relatorio(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Relatório de Desempenho", font=("Arial", 14))
        label.pack(pady=20)

        if not self.tempo_execucao:
            tk.Label(self.root, text="Nenhum relatório disponível.").pack()
            btn_menu = tk.Button(self.root, text="Voltar ao Menu", command=self.menu_inicial)
            btn_menu.pack(pady=10)
            return

        # Mostra os resultados de cada busca e destacando o titulo de cada busca
        for i, resultados in enumerate(self.resultados):
            if i == 0:
                titulo = "Busca em Largura"
            elif i == 1:
                titulo = "Busca em Profundidade"
            elif i == 2:
                titulo = "Busca A*"
            elif i == 3:
                titulo = "Busca Gulosa"
            tk.Label(self.root, text=titulo, font=("Arial", 12, "bold")).pack()
            tk.Label(self.root, text=f"Tempo de Execução: {resultados[0]} nos visitados").pack()
            tk.Label(self.root, text=f"Custo de Tempo: {resultados[0]}").pack()
            tk.Label(self.root, text=f"Custo de Espaço: {resultados[1]}").pack()
            tk.Label(self.root, text=f"Nós Gerados: {resultados[2]}").pack()
            tk.Label(self.root, text=f"Profundidade da Busca: {resultados[3]}").pack()
            tk.Label(self.root, text=f"Profundidade da Solução: {resultados[4]}").pack()

        btn_menu = tk.Button(self.root, text="Voltar ao Menu", command=self.menu_inicial)
        btn_menu.pack(pady=10)

        #salvando os resultados em um arquivo
        with open("relatorio.txt", "w") as arquivo:
            arquivo.write("Relatório de Desempenho\n")
            for i, resultados in enumerate(self.resultados):
                if i == 0:
                    titulo = "Busca em Largura"
                elif i == 1:
                    titulo = "Busca em Profundidade"
                elif i == 2:
                    titulo = "Busca A*"
                elif i == 3:
                    titulo = "Busca Gulosa"
                arquivo.write(f"{titulo}\n")
                arquivo.write(f"Tempo de Execução: {resultados[0]} nos visitados\n")
                arquivo.write(f"Custo de Tempo: {resultados[0]}\n")
                arquivo.write(f"Custo de Espaço: {resultados[1]}\n")
                arquivo.write(f"Nós Gerados: {resultados[2]}\n")
                arquivo.write(f"Profundidade da Busca: {resultados[3]}\n")
                arquivo.write(f"Profundidade da Solução: {resultados[4]}\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoDos8Numeros(root)
    root.mainloop()
