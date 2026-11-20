"""
Pilha (LIFO: "Last-In, First-Out") — implementação DINÂMICA.  [Aula 06, slides 24-31]

            topo
             |
             v
          +----+---+    +----+---+    +----+---+
          | A3 | o-+--> | A2 | o-+--> | A1 | / |
          +----+---+    +----+---+    +----+---+
       (último a entrar = primeiro a sair)

No jogo, a pilha aparece em dois papéis:
    1. Histórico de ações -> "desfazer" sempre desfaz a ação MAIS RECENTE.
    2. DFS iterativa      -> substitui a pilha de chamadas da recursão
                             ("Simulação de recursão com pilha", aula 06).

Todas as operações são O(1).
"""

from estruturas.no import No


class Pilha:
    def __init__(self):
        self.topo = None            # pilha vazia: topo = NULL
        self.tamanho = 0
        self.maior_tamanho = 0      # métrica pedida no EP (seção 15.1)

    def esta_vazia(self):
        return self.topo is None

    def push(self, chave):
        """
        push (pilha, x)                                [Aula 06, slide 30]
        1. x.prox <- pilha.topo
        2. pilha.topo <- x
        """
        x = No(chave)
        x.prox = self.topo      # 1: o novo nó aponta para o antigo topo
        self.topo = x           # 2: o novo nó passa a ser o topo
        self.tamanho += 1
        self.maior_tamanho = max(self.maior_tamanho, self.tamanho)

    def pop(self):
        """
        pop (pilha, t)                                 [Aula 06, slide 31]
        1. se (pilha.topo = NULL) então //pilha vazia
        2.     retorna false
        3. t <- pilha.topo.chave
        4. pilha.topo <- pilha.topo.prox
        5. retorna true
        Em Python devolvemos o par (sucesso, valor): (True, t) ou (False, None).
        """
        if self.topo is None:           # 1
            return False, None          # 2: pilha vazia, nada é alterado
        t = self.topo.chave             # 3
        self.topo = self.topo.prox      # 4
        self.tamanho -= 1
        return True, t                  # 5

    def peek(self):
        """Consulta o topo sem remover: (True, valor) ou (False, None)."""
        if self.topo is None:
            return False, None
        return True, self.topo.chave

    def para_lista(self):
        """Elementos do topo para a base (para exibir na tela)."""
        itens, p = [], self.topo
        while p is not None:
            itens.append(p.chave)
            p = p.prox
        return itens

    def __len__(self):
        return self.tamanho

    def __str__(self):
        if self.esta_vazia():
            return "topo -> (vazia)"
        return "topo -> " + " | ".join(str(c) for c in self.para_lista())
