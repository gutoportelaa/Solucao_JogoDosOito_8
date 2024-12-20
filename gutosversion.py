import tkinter as tk
import random
import time
import matplotlib.pyplot as plt
from collections import deque
import heapq  # Pra busca A*
import pprint


def imprimir_arvore(arvore, profundidade=0):
    """Função recursiva para imprimir árvore hierárquica de busca."""
    if isinstance(arvore, dict):
        for chave, subarvore in arvore.items():
            print("    " * profundidade + f"Movimento: {chave}")
            imprimir_arvore(subarvore, profundidade + 1)
    else:
        print("    " * profundidade + f"Estado: {arvore}")
        
def imprimir_tabuleiro(estado):
    """Exibe o estado atual do tabuleiro de 3x3 no terminal."""
    for i in range(0, 9, 3):
        linha = estado[i:i+3]
        print(" | ".join(str(x) if x != '' else ' ' for x in linha))
        if i < 6:
            print("-" * 9)

class JogoDos8Numeros:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo dos 8 Números")
        self.movimentos = 0
        self.modo_jogo = None
        self.sequencia_vitoria = [1, 2, 3, 4, 5, 6, 7, 8, '']
        self.caminho_solucao = []
        self.tabuleiro_inicial = []
        self.tempo_execucao = {}
        self.nos_gerados = {}
        self.nos_fronteira = {}
        self.profundidade_solucao = {}
        self.profundidade_maxima = {}  # Adicione esta linha
        self.tabuleiro = []
        self.menu_inicial()



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

    def iniciar_jogo_agente(self, tipo_busca):
        self.modo_jogo = tipo_busca
        self.iniciar_jogo()

        # Registra o tempo e coleta dados adicionais
        inicio = time.time()
        if self.modo_jogo == 'largura':
            self.busca_em_largura()
        elif self.modo_jogo == 'profundidade':
            self.busca_em_profundidade()
        elif self.modo_jogo == 'gulosa':
            self.busca_gulosa()
        elif self.modo_jogo == 'a_estrela':
            self.busca_a_estrela()
        fim = time.time()

        self.tempo_execucao[self.modo_jogo] = fim - inicio
        
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
    
    
    
        
    #     # Função para imprimir árvore
    # def imprimir_arvore(arvore, profundidade=0):
    #     """Função recursiva para imprimir árvore hierárquica de busca."""
    #     if isinstance(arvore, dict):
    #         for chave, subarvore in arvore.items():
    #             print("    " * profundidade + f"Movimento: {chave}")
    #             imprimir_arvore(subarvore, profundidade + 1)
    #     else:
    #         print("    " * profundidade + f"Estado: {arvore}")

    def busca_em_largura(self):
        """Executa a busca em largura e imprime apenas os movimentos realizados no caminho da solução."""
        inicio = time.time()  # Marca o início do tempo
        fila = deque([(self.tabuleiro, [], 0)])  # 0 = profundidade inicial
        visitados = set()
        nos_gerados = 0
        max_fronteira = 0  # Armazena o tamanho máximo da fronteira
        profundidade_maxima = 0  # Armazena a profundidade máxima atingida

        while fila:
            estado_atual, caminho, profundidade = fila.popleft()

            # Verifica se atingimos o estado de vitória
            if estado_atual == self.sequencia_vitoria:
                self.caminho_solucao = caminho
                self.profundidade_solucao['largura'] = profundidade
                self.executar_caminho(caminho)
                print("Solução encontrada!")
                break

            # Adiciona o estado atual aos visitados e expande
            if tuple(estado_atual) not in visitados:
                visitados.add(tuple(estado_atual))
                nos_gerados += 1
                index_vazio = estado_atual.index('')
                profundidade_maxima = max(profundidade_maxima, profundidade)  # Atualiza a profundidade máxima atingida
                
                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    fila.append((novo_estado, caminho + [movimento], profundidade + 1))
                    max_fronteira = max(max_fronteira, len(fila))  # Atualiza o tamanho máximo da fronteira

        # Marca o final do tempo e calcula o tempo de execução
        fim = time.time()
        self.tempo_execucao['largura'] = fim - inicio
        self.nos_gerados['largura'] = nos_gerados
        self.nos_fronteira['largura'] = max_fronteira
        self.profundidade_maxima['largura'] = profundidade_maxima

        print("\nPasso-a-passo da Solução (Movimentos Executados) - Busca em Profundidade:")
        for passo, movimento in enumerate(self.caminho_solucao, start=1):
            print(f"Passo {passo}: Movimento para posição {movimento}")
            imprimir_tabuleiro(self.tabuleiro)

        # Exibe o relatório detalhado após a execução
        print("\n--- Relatório da Busca em Largura ---")
        print(f"Tempo de Execução: {self.tempo_execucao['largura']:.4f} segundos")
        print(f"Nós Gerados: {self.nos_gerados['largura']}")
        print(f"Uso de Memória (Máximo da Fronteira): {self.nos_fronteira['largura']} estados")
        print(f"Profundidade da Solução: {self.profundidade_solucao['largura']}")
        print(f"Profundidade Máxima Atingida: {self.profundidade_maxima['largura']}")
        print("Optimalidade: Sim, pois encontra o caminho mais curto.")
        print("Completude: Sim, pois sempre encontrará a solução se existir.")



        # # Imprime a árvore ao final da busca
        # print("\nÁrvore de Busca em Largura:")
        # imprimir_arvore(arvore_busca)

    def busca_em_profundidade(self):
        """Executa a busca em profundidade e imprime apenas os movimentos realizados no caminho da solução."""
        inicio = time.time()
        profundidade_maxima = 100
        visitados = set()
        nos_gerados = 0
        max_fronteira = 0
        profundidade_maxima_atingida = 0

        def profundidade_limitada(estado_atual, caminho, profundidade):
            nonlocal nos_gerados, max_fronteira, profundidade_maxima_atingida

            # Verifica se atingimos o estado de vitória
            if estado_atual == self.sequencia_vitoria:
                self.caminho_solucao = caminho
                self.profundidade_solucao['profundidade'] = profundidade
                self.executar_caminho(caminho)
                return True

            # Limita a profundidade para evitar loops infinitos
            if profundidade >= profundidade_maxima:
                return False

            visitados.add(tuple(estado_atual))
            nos_gerados += 1
            profundidade_maxima_atingida = max(profundidade_maxima_atingida, profundidade)

            index_vazio = estado_atual.index('')
            for movimento in self.movimentos_permitidos(index_vazio):
                novo_estado = estado_atual[:]
                novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                
                # Executa busca recursiva se o estado ainda não foi visitado
                if tuple(novo_estado) not in visitados:
                    max_fronteira = max(max_fronteira, len(visitados))
                    if profundidade_limitada(novo_estado, caminho + [movimento], profundidade + 1):
                        return True
            visitados.remove(tuple(estado_atual))
            return False

        profundidade_limitada(self.tabuleiro, [], 0)
        fim = time.time()

        # Registra as métricas de desempenho
        self.tempo_execucao['profundidade'] = fim - inicio
        self.nos_gerados['profundidade'] = nos_gerados
        self.nos_fronteira['profundidade'] = max_fronteira
        self.profundidade_maxima['profundidade'] = profundidade_maxima_atingida

        # Exibe o passo-a-passo e o relatório
        print("\nPasso-a-passo da Solução (Movimentos Executados) - Busca em Profundidade:")
        for passo, movimento in enumerate(self.caminho_solucao, start=1):
            print(f"Passo {passo}: Movimento para posição {movimento}")
            imprimir_tabuleiro(self.tabuleiro)

        print("\n--- Relatório da Busca em Profundidade ---")
        print(f"Tempo de Execução: {self.tempo_execucao['profundidade']:.4f} segundos")
        print(f"Nós Gerados: {self.nos_gerados['profundidade']}")
        print(f"Uso de Memória (Máximo da Fronteira): {self.nos_fronteira['profundidade']} estados")
        print(f"Profundidade da Solução: {self.profundidade_solucao['profundidade']}")
        print(f"Profundidade Máxima Atingida: {self.profundidade_maxima['profundidade']}")
        print("Optimalidade: Não, pois pode não encontrar o caminho mais curto.")
        print("Completude: Sim, até a profundidade máxima definida.")

            
    def busca_a_estrela(self):
        """Executa a busca A* e imprime o caminho da solução."""
        inicio = time.time()
        nos_gerados = 0
        max_fronteira = 0
        visitados = set()

        def h(estado):
            """Heurística: número de peças fora do lugar."""
            return sum(1 for i, j in zip(estado, self.sequencia_vitoria) if i != j and i != '')

        # Converte o estado inicial para usar 0 temporariamente para o espaço vazio
        estado_inicial = [0 if x == '' else x for x in self.tabuleiro]
        fila = [(h(estado_inicial), 0, estado_inicial, [])]

        while fila:
            _, custo, estado_atual, caminho = heapq.heappop(fila)

            # Verifica se o estado atual é o estado de vitória
            if estado_atual == [0 if x == '' else x for x in self.sequencia_vitoria]:
                self.caminho_solucao = caminho
                self.executar_caminho(caminho)
                break

            if tuple(estado_atual) not in visitados:
                visitados.add(tuple(estado_atual))
                nos_gerados += 1
                index_vazio = estado_atual.index(0)

                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    novo_custo = custo + 1
                    heapq.heappush(fila, (novo_custo + h(novo_estado), novo_custo, novo_estado, caminho + [movimento]))
                    max_fronteira = max(max_fronteira, len(fila))

        fim = time.time()
        self.tempo_execucao['a_estrela'] = fim - inicio
        self.nos_gerados['a_estrela'] = nos_gerados
        self.nos_fronteira['a_estrela'] = max_fronteira

        print("\nPasso-a-passo da Solução (Movimentos Executados) - Busca A*:")
        for passo, movimento in enumerate(self.caminho_solucao, start=1):
            print(f"Passo {passo}: Movimento para posição {movimento}")
            imprimir_tabuleiro(self.tabuleiro)

        print("\n--- Relatório da Busca A* ---")
        print(f"Tempo de Execução: {self.tempo_execucao['a_estrela']:.4f} segundos")
        print(f"Nós Gerados: {self.nos_gerados['a_estrela']}")
        print(f"Uso de Memória (Máximo da Fronteira): {self.nos_fronteira['a_estrela']} estados")
        print("Admissibilidade: Sim, pois a heurística é consistente.")
        print("Optimalidade: Sim, encontra o caminho mais curto.")
        print("Completude: Sim, para tabuleiros finitos.")

    def busca_gulosa(self):
        """Executa a busca gulosa e imprime o caminho da solução."""
        inicio = time.time()
        nos_gerados = 0
        max_fronteira = 0
        visitados = set()

        def h(estado):
            """Heurística: número de peças fora do lugar."""
            return sum(1 for i, j in zip(estado, self.sequencia_vitoria) if i != j and i != '')

        # Converte o estado inicial para usar 0 temporariamente para o espaço vazio
        estado_inicial = [0 if x == '' else x for x in self.tabuleiro]
        fila = [(h(estado_inicial), estado_inicial, [])]

        while fila:
            _, estado_atual, caminho = heapq.heappop(fila)

            # Verifica se o estado atual é o estado de vitória
            if estado_atual == [0 if x == '' else x for x in self.sequencia_vitoria]:
                self.caminho_solucao = caminho
                self.executar_caminho(caminho)
                break

            if tuple(estado_atual) not in visitados:
                visitados.add(tuple(estado_atual))
                nos_gerados += 1
                index_vazio = estado_atual.index(0)

                for movimento in self.movimentos_permitidos(index_vazio):
                    novo_estado = estado_atual[:]
                    novo_estado[index_vazio], novo_estado[movimento] = novo_estado[movimento], novo_estado[index_vazio]
                    heapq.heappush(fila, (h(novo_estado), novo_estado, caminho + [movimento]))
                    max_fronteira = max(max_fronteira, len(fila))

        fim = time.time()
        self.tempo_execucao['gulosa'] = fim - inicio
        self.nos_gerados['gulosa'] = nos_gerados
        self.nos_fronteira['gulosa'] = max_fronteira

        print("\nPasso-a-passo da Solução (Movimentos Executados) - Busca Gulosa:")
        for passo, movimento in enumerate(self.caminho_solucao, start=1):
            print(f"Passo {passo}: Movimento para posição {movimento}")
            imprimir_tabuleiro(self.tabuleiro)

        print("\n--- Relatório da Busca Gulosa ---")
        print(f"Tempo de Execução: {self.tempo_execucao['gulosa']:.4f} segundos")
        print(f"Nós Gerados: {self.nos_gerados['gulosa']}")
        print(f"Uso de Memória (Máximo da Fronteira): {self.nos_fronteira['gulosa']} estados")
        print("Admissibilidade: Não garantida, depende da heurística.")
        print("Optimalidade: Não, pois a solução pode não ser a mais curta.")
        print("Completude: Sim, para tabuleiros finitos.")


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
