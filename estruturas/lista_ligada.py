"""
Lista simplesmente ligada "COM CABEÇA".          [Aula 06, slides 6-23]

    cabeca          1º            2º            3º
    +----+---+    +----+---+    +----+---+    +----+---+
    | -- | o-+--> | E2 | o-+--> | E4 | o-+--> | E1 | / |
    +----+---+    +----+---+    +----+---+    +----+---+
                                                 ^
                                              ultimo

Por que "com cabeça"?
    O nó cabeça não guarda dado; só marca o início. Assim, inserir ou remover
    no primeiro nó funciona igual a inserir/remover em qualquer outro lugar.
    Na aula: "Listas com cabeça não reduzem a complexidade assintótica, mas
    simplificam a implementação dos algoritmos."

Por que "simplesmente ligada" e não duplamente?            [decisão da equipe]
    No jogo a lista de custódia só é percorrida do início para o fim.
    Um ponteiro por nó basta e o código fica mais curto.
    Custo: remover o último nó é O(n), porque é preciso achar o penúltimo.

Acréscimo da equipe: ponteiro "ultimo".
    Permite inserir no fim em O(1) (a custódia sempre cresce pelo fim).

Complexidades:
    inserir_inicio, inserir_fim, primeiro, ultimo_elemento ... O(1)
    buscar, remover, inserir_apos, remover_fim ............... O(n)
"""

from estruturas.no import No


class ListaLigada:
    def __init__(self):
        self.cabeca = No(None)   # nó cabeça: conteúdo "irrelevante"
        self.ultimo = None       # último nó com dado (None se vazia)
        self.tamanho = 0

    # ------------------------------------------------------------ consultas
    def esta_vazia(self):
        return self.cabeca.prox is None

    def primeiro(self):
        """Consulta o início. Devolve (True, chave) ou (False, None) se vazia."""
        if self.esta_vazia():
            return False, None
        return True, self.cabeca.prox.chave

    def ultimo_elemento(self):
        """Consulta o fim. Devolve (True, chave) ou (False, None) se vazia."""
        if self.esta_vazia():
            return False, None
        return True, self.ultimo.chave

    def buscar(self, k):
        """
        busca (L, k)                                   [Aula 06, slide 20]
        1. p <- L.prox
        2. enquanto (p != NULL e p.chave != k) faça
        3.     p <- p.prox
        4. retorna p
        Devolve o nó que contém k, ou None se k não está na lista.  O(n)
        """
        p = self.cabeca.prox                     # 1
        while p is not None and p.chave != k:    # 2
            p = p.prox                           # 3
        return p                                 # 4

    def contem(self, k):
        return self.buscar(k) is not None

    def percorrer(self):
        """Visita todos os nós, do início ao fim, e devolve as chaves. O(n)"""
        chaves = []
        p = self.cabeca.prox
        while p is not None:
            chaves.append(p.chave)
            p = p.prox
        return chaves

    # ------------------------------------------------------------ inserções
    def inserir_inicio(self, chave):
        """
        insere (L, x)                                  [Aula 06, slide 18]
        1. x.prox <- L.prox
        2. L.prox <- x
        O(1). Graças à cabeça, lista vazia e não vazia são o mesmo caso.
        """
        x = No(chave)
        x.prox = self.cabeca.prox   # 1
        self.cabeca.prox = x        # 2
        if self.ultimo is None:     # a lista estava vazia: x também é o último
            self.ultimo = x
        self.tamanho += 1

    def inserir_fim(self, chave):
        """Insere após o último nó. O(1) graças ao ponteiro 'ultimo'."""
        x = No(chave)
        if self.ultimo is None:     # lista vazia: o "anterior" é a cabeça
            self.cabeca.prox = x
        else:
            self.ultimo.prox = x
        self.ultimo = x
        self.tamanho += 1

    def inserir_apos(self, chave_referencia, chave):
        """
        Insere 'chave' logo depois do nó que contém 'chave_referencia'.
        Devolve True se inseriu; False se a referência não existe. O(n)
        """
        p = self.buscar(chave_referencia)
        if p is None:
            return False
        x = No(chave)
        x.prox = p.prox
        p.prox = x
        if p is self.ultimo:
            self.ultimo = x
        self.tamanho += 1
        return True

    # ------------------------------------------------------------ remoções
    def remover(self, k):
        """
        remove (L, k)                                  [Aula 06, slide 23]
        1. p <- L
        2. q <- L.prox
        3. enquanto (q != NULL e q.chave != k) faça
        4.     p <- q
        5.     q <- q.prox
        6. se (q != NULL) então  //achou k
        7.     p.prox <- q.prox
        Devolve True se removeu; False se k não estava na lista. O(n)
        """
        p = self.cabeca                          # 1
        q = self.cabeca.prox                     # 2
        while q is not None and q.chave != k:    # 3
            p = q                                # 4
            q = q.prox                           # 5
        if q is None:                            # k não está na lista
            return False
        p.prox = q.prox                          # 7: "pula" o nó q
        if q is self.ultimo:                     # removemos o último
            self.ultimo = p if p is not self.cabeca else None
        self.tamanho -= 1
        return True

    def remover_inicio(self):
        """Remove o 1º nó. Devolve (True, chave) ou (False, None). O(1)"""
        if self.esta_vazia():
            return False, None
        chave = self.cabeca.prox.chave
        self.remover(chave)   # o 1º nó é encontrado na primeira comparação
        return True, chave

    def remover_fim(self):
        """Remove o último nó. Devolve (True, chave) ou (False, None). O(n)"""
        if self.esta_vazia():
            return False, None
        p = self.cabeca                 # procura o penúltimo
        while p.prox is not self.ultimo:
            p = p.prox
        chave = self.ultimo.chave
        p.prox = None
        self.ultimo = p if p is not self.cabeca else None
        self.tamanho -= 1
        return True, chave

    # ------------------------------------------------------------ exibição
    def __len__(self):
        return self.tamanho

    def __str__(self):
        if self.esta_vazia():
            return "[cabeça] -> NULL"
        return "[cabeça] -> " + " -> ".join(str(c) for c in self.percorrer()) + " -> NULL"
