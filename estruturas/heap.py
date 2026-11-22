"""
Fila de prioridade com HEAP BINÁRIO DE MÍNIMO.   [Aula 08, slides 23-45]

Por que heap? (Aula 08, slide 24)
    Com lista NÃO ordenada: inserir O(1), extrair o menor O(n).
    Com lista ORDENADA:     inserir O(n), extrair o menor O(1).
    Com HEAP:               inserir O(log n) e extrair o menor O(log n).

O que é (slides 26-28)
    Árvore binária QUASE COMPLETA guardada num VETOR. A aula detalha o heap de
    MÁXIMO e diz que ele "pode ser facilmente adaptado" para o de MÍNIMO: basta
    inverter as comparações. Aqui usamos o de MÍNIMO, porque o Dijkstra (aula 11)
    precisa de Extrai-Min: sempre o vértice com a MENOR distância estimada.

    Vetor começa na posição 1 (a posição 0 fica vazia), como no slide 30:
        pai de k        = k // 2          (quociente inteiro)
        filho esquerdo  = 2k
        filho direito   = 2k + 1

            (2)                 posição: 1   2   3   4   5
           /   \\               vetor  : 2 | 5 | 3 | 9 | 7
         (5)   (3)
         / \\
       (9) (7)          cada pai é MENOR OU IGUAL aos seus filhos

Cuidado (slide 28): heap NÃO é árvore binária de busca. Num heap só se sabe
que o pai é menor ou igual aos filhos; não há ordem entre irmãos.

Cada elemento é guardado como (prioridade, ordem_de_chegada, item). A ordem de
chegada desempata prioridades iguais, para o resultado ser sempre o mesmo.
"""


class HeapMinimo:
    def __init__(self):
        self.heap = [None]          # posição 0 vazia: o heap começa em 1 (slide 30)
        self.n = 0
        self.posicao = {}           # item -> posição no vetor (para diminuir_chave)
        self._chegada = 0
        self.maior_tamanho = 0      # métrica (seção 15.1 do EP)
        self.trocas = 0             # quantas trocas pai <-> filho foram feitas

    def __len__(self):
        return self.n

    def esta_vazio(self):
        return self.n == 0

    def contem(self, item):
        return item in self.posicao

    def prioridade(self, item):
        return self.heap[self.posicao[item]][0]

    # ------------------------------------------------------------------ apoio
    def _menor(self, i, j):
        return self.heap[i][:2] < self.heap[j][:2]

    def _trocar(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.posicao[self.heap[i][2]] = i
        self.posicao[self.heap[j][2]] = j
        self.trocas += 1

    # ------------------------------------------------------------------ inserir
    def inserir(self, item, prioridade):
        """
        insere (heap[1..n], elemento)                    [Aula 08, slide 35]
        1. heap[n + 1] <- elemento
        2. n <- n + 1
        3. subir (n)
        Complexidade: igual à de subir(): O(log n).
        """
        if item in self.posicao:
            raise ValueError(f"{item!r} já está no heap; use diminuir_chave")
        self._chegada += 1
        self.heap.append((prioridade, self._chegada, item))     # 1
        self.n += 1                                             # 2
        self.posicao[item] = self.n
        self.maior_tamanho = max(self.maior_tamanho, self.n)
        self._subir(self.n)                                     # 3

    def _subir(self, filho):
        """
        subir (filho)                                    [Aula 08, slide 36]
        1. pai <- ⌊filho/2⌋
        2. se (pai >= 1) então                  //pai está dentro do heap
        3.     se (heap[filho] > heap[pai]) então   //troca pai e filho
        4.         heap[filho] <-> heap[pai]
        5.         subir (pai)
        Adaptação para MÍNIMO, linha 3: troca se heap[filho] < heap[pai].
        """
        pai = filho // 2                                        # 1
        if pai >= 1:                                            # 2
            if self._menor(filho, pai):                         # 3 (invertido)
                self._trocar(filho, pai)                        # 4
                self._subir(pai)                                # 5

    # ------------------------------------------------------------------ remover
    def extrair_minimo(self):
        """
        remove (heap[1..n])                              [Aula 08, slide 44]
        1. heap[1] <- heap[n]
        2. n <- n - 1
        3. descer (1)
        Antes da linha 1 guardamos heap[1] (a raiz = o MENOR), que é devolvido.
        Devolve (True, item, prioridade); com o heap vazio, (False, None, None),
        no mesmo padrão da pilha e da fila (aula 06).
        """
        if self.n == 0:
            return False, None, None
        prioridade, _, item = self.heap[1]
        del self.posicao[item]
        ultimo = self.heap.pop()
        self.n -= 1                                             # 2
        if self.n >= 1:
            self.heap[1] = ultimo                               # 1
            self.posicao[ultimo[2]] = 1
            self._descer(1)                                     # 3
        return True, item, prioridade

    def _descer(self, pai):
        """
        descer (pai)                                     [Aula 08, slide 45]
        1. filho <- 2 * pai                      //filho esquerdo
        2. se (filho <= n) então                 //filho está dentro do heap
        3.     se (filho < n) então              //tem irmão à direita
        4.         se (heap[filho + 1] > heap[filho]) então
        5.             filho <- filho + 1        //fica com o filho MAIOR
        6.     se (heap[pai] < heap[filho]) então    //troca pai e filho
        7.         heap[pai] <-> heap[filho]
        8.         descer (filho)
        Adaptação para MÍNIMO, linhas 4 e 6: escolhe o filho MENOR e troca se
        ele for menor que o pai. Complexidade: O(log n).
        """
        filho = 2 * pai                                         # 1
        if filho <= self.n:                                     # 2
            if filho < self.n:                                  # 3
                if self._menor(filho + 1, filho):               # 4 (invertido)
                    filho = filho + 1                           # 5
            if self._menor(filho, pai):                         # 6 (invertido)
                self._trocar(pai, filho)                        # 7
                self._descer(filho)                             # 8

    # ------------------------------------------------------------------ atualizar
    def diminuir_chave(self, item, nova_prioridade):
        """
        Usada pelo Dijkstra quando relaxa(u, v, w) melhora d[v]. A aula 11
        (slide 27, análise com heap) diz que "o heap permite atualizar os valores com
        custo O(log |V|)": o elemento recebe prioridade menor e SOBE.
        """
        k = self.posicao[item]
        _, chegada, _ = self.heap[k]
        self.heap[k] = (nova_prioridade, chegada, item)
        self._subir(k)

    # ------------------------------------------------------------------ conferência
    def eh_heap(self):
        """Confere a propriedade: todo pai <= seus filhos (usado nos testes)."""
        for k in range(2, self.n + 1):
            if self._menor(k, k // 2):
                return False
        return all(self.posicao[self.heap[k][2]] == k for k in range(1, self.n + 1))

    def vetor(self):
        """Prioridades na ordem do vetor (posição 1 em diante), para exibir."""
        return [p for p, _, _ in self.heap[1:]]

    def itens(self):
        """(item, prioridade) na ordem do vetor, para exibir o heap passo a passo."""
        return [(item, p) for p, _, item in self.heap[1:]]

    def __str__(self):
        return "heap[1..n] = " + " | ".join(f"{item}:{p}" for p, _, item in self.heap[1:])
