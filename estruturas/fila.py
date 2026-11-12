"""
Fila (FIFO: "First-In, First-Out") — implementação DINÂMICA.  [Aula 06, slides 51-59]

        inicio                                final
          |                                     |
          v                                     v
       +----+---+    +----+---+    +----+---+
       | E1 | o-+--> | E2 | o-+--> | E3 | / |
       +----+---+    +----+---+    +----+---+
    sai por aqui (dequeue)          entra por aqui (enqueue)

No jogo, a fila aparece em dois papéis:
    1. Fila de entrada da Central de Triagem (evidências na ordem de chegada).
    2. BFS -> garante que os estados são explorados "por camadas":
       primeiro todos a 1 passo, depois todos a 2 passos, e assim por diante.

Todas as operações são O(1).
"""

from estruturas.no import No


class Fila:
    def __init__(self):
        self.inicio = None
        self.final = None
        self.tamanho = 0
        self.maior_tamanho = 0      # métrica pedida no EP (seção 15.1)

    def esta_vazia(self):
        return self.inicio is None

    def enqueue(self, chave):
        """
        enqueue (fila, x)                              [Aula 06, slide 58]
        1. se (fila.final = NULL) então //fila vazia
        2.     x.prox <- NULL
        3.     fila.inicio <- x
        4.     fila.final <- x
        5. senão //fila não vazia
        6.     x.prox <- NULL
        7.     fila.final.prox <- x
        8.     fila.final <- x
        """
        x = No(chave)                  # 2/6: No() já nasce com prox = None
        if self.final is None:         # 1
            self.inicio = x            # 3
            self.final = x             # 4
        else:                          # 5
            self.final.prox = x        # 7
            self.final = x             # 8
        self.tamanho += 1
        self.maior_tamanho = max(self.maior_tamanho, self.tamanho)

    def dequeue(self):
        """
        dequeue (fila, i)                              [Aula 06, slide 59]
        1. se (fila.inicio = NULL) então //fila vazia
        2.     retorna false
        3. i <- fila.inicio.chave
        4. fila.inicio <- fila.inicio.prox
        5. se (fila.inicio = NULL) então //fila ficou vazia
        6.     fila.final <- NULL
        7. retorna true
        Em Python devolvemos o par (sucesso, valor): (True, i) ou (False, None).
        """
        if self.inicio is None:              # 1
            return False, None               # 2
        i = self.inicio.chave                # 3
        self.inicio = self.inicio.prox       # 4
        if self.inicio is None:              # 5
            self.final = None                # 6
        self.tamanho -= 1
        return True, i                       # 7

    def peek(self):
        """front/peek: consulta o próximo a sair, sem remover."""
        if self.inicio is None:
            return False, None
        return True, self.inicio.chave

    def para_lista(self):
        """Elementos do início para o final (para exibir na tela)."""
        itens, p = [], self.inicio
        while p is not None:
            itens.append(p.chave)
            p = p.prox
        return itens

    def __len__(self):
        return self.tamanho

    def __str__(self):
        if self.esta_vazia():
            return "início -> (vazia) <- final"
        return "início -> " + " | ".join(str(c) for c in self.para_lista()) + " <- final"
