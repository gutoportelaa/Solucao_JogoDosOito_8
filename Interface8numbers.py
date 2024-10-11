import tkinter as tk
import random

class JogoDos8Numeros:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo dos 8 Números")
        
        # Cria uma matriz 3x3 para armazenar os números
        self.tabuleiro = [1, 2, 3, 4, 5, 6, 7, 8, '']
        random.shuffle(self.tabuleiro)  # Embaralha os números no tabuleiro
        
        # Cria os botões da interface
        self.botoes = []
        for i in range(9):
            botao = tk.Button(self.root, text=str(self.tabuleiro[i]), width=10, height=5, command=lambda i=i: self.mover(i))
            botao.grid(row=i//3, column=i%3)
            self.botoes.append(botao)

    def atualizar_botoes(self):
        # Atualiza os textos dos botões conforme a posição do tabuleiro
        for i in range(9):
            self.botoes[i].config(text=str(self.tabuleiro[i]) if self.tabuleiro[i] != '' else '')

    def mover(self, i):
        # Verifica a posição do espaço vazio
        index_vazio = self.tabuleiro.index('')
        
        # Lista de movimentos permitidos com base na posição do botão clicado
        movimentos_permitidos = {
            0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
            3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
            6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
        }
        
        # Se o botão clicado estiver ao lado do espaço vazio, move o número
        if index_vazio in movimentos_permitidos[i]:
            self.tabuleiro[index_vazio], self.tabuleiro[i] = self.tabuleiro[i], self.tabuleiro[index_vazio]
            self.atualizar_botoes()

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoDos8Numeros(root)
    root.mainloop()
