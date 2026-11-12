"""
Árvore AVL (Adelson-Velsky e Landis).             [Aula 08, slides 3-21]

Uma árvore binária de busca é AVL quando, para TODO nó x,
        | hE(x) - hD(x) | <= 1
(as alturas das subárvores esquerda e direita diferem no máximo em 1).

    Fator de balanceamento:  FB(x) = hE(x) - hD(x)   ->  só pode ser -1, 0 ou +1
    Altura da árvore vazia:  -1                       [Aula 07, slide 15]

Por que AVL no jogo?
    O solver precisa responder milhares de vezes à pergunta
    "já visitei este estado?". Numa lista, cada pergunta custa O(n).
    Na AVL, a altura fica sempre O(log n), então busca e inserção custam
    O(log n). Com 1.000 estados: ~1.000 comparações na lista,
    no máximo ~14 na AVL (altura máxima de uma AVL com n nós ~ 1,44 log2 n).

Quando a inserção desbalanceia um nó p (FB = +2 ou -2), uma de 4 rotações
corrige:
    FB(p) = +2, inserção na esquerda da esquerda  ("reta")  -> RD
    FB(p) = -2, inserção na direita da direita    ("reta")  -> RE
    FB(p) = +2, inserção na direita da esquerda   ("curva") -> RED (dupla)
    FB(p) = -2, inserção na esquerda da direita   ("curva") -> RDE (dupla)
"""


class NoAVL:
    """Nó da AVL: (esq, chave, dir) como na aula 07, mais a altura h."""

    def __init__(self, chave, valor=None):
        self.chave = chave      # chave comparável (no jogo: a chave do estado)
        self.valor = valor      # dado associado (opcional)
        self.esq = None
        self.dir = None
        self.h = 0              # um nó sozinho (folha) tem altura 0


def altura(r):
    """Altura guardada no nó; árvore vazia (NULL) tem altura -1. O(1)"""
    return -1 if r is None else r.h


def fator_balanceamento(r):
    """FB = hE - hD  (aula 08, slide 4)."""
    return altura(r.esq) - altura(r.dir)


class ArvoreAVL:
    def __init__(self):
        self.raiz = None
        self.quantidade = 0
        self.rotacoes = {"RD": 0, "RE": 0, "RED": 0, "RDE": 0}
        self.historico_rotacoes = []   # [(tipo, chave do nó p)] para o relatório
        self._inseriu = False

    # ============================================================ rotações
    def _rotacao_direita(self, p):
        """
        rotacaoDireita (p)                             [Aula 08, slide 16]
        1. u <- p.esq
        2. p.esq <- u.dir
        3. u.dir <- p
        4. p.h <- max(altura(p.esq), altura(p.dir)) + 1
        5. u.h <- max(altura(u.esq), p.h) + 1
        6. retorna u
                p                u
               / \\             / \\
              u   T3   ==>    T1   p
             / \\                  / \\
           T1   T2               T2   T3
        """
        u = p.esq                                         # 1
        p.esq = u.dir                                     # 2
        u.dir = p                                         # 3
        p.h = max(altura(p.esq), altura(p.dir)) + 1       # 4
        u.h = max(altura(u.esq), p.h) + 1                 # 5
        return u                                          # 6

    def _rotacao_esquerda(self, p):
        """
        rotacaoEsquerda (p)                            [Aula 08, slide 17]
        1. y <- p.dir
        2. p.dir <- y.esq
        3. y.esq <- p
        4. p.h <- max(altura(p.esq), altura(p.dir)) + 1
        5. y.h <- max(p.h, altura(y.dir)) + 1
        6. retorna y
              p                    y
             / \\                  / \\
           T1   y      ==>       p   T3
               / \\              / \\
             T2   T3          T1   T2
        """
        y = p.dir                                         # 1
        p.dir = y.esq                                     # 2
        y.esq = p                                         # 3
        p.h = max(altura(p.esq), altura(p.dir)) + 1       # 4
        y.h = max(p.h, altura(y.dir)) + 1                 # 5
        return y                                          # 6

    def _rotacao_esquerda_direita(self, p):
        """
        rotacaoEsquerdaDireita (p)                     [Aula 08, slide 18]
        1. u <- p.esq
        2. p.esq <- rotacaoEsquerda(u)
        3. retorna rotacaoDireita(p)
        Rotação dupla = composição de duas rotações simples.
        """
        u = p.esq                                         # 1
        p.esq = self._rotacao_esquerda(u)                 # 2
        return self._rotacao_direita(p)                   # 3

    def _rotacao_direita_esquerda(self, p):
        """
        rotacaoDireitaEsquerda (p)                     [Aula 08, slide 19]
        1. y <- p.dir
        2. p.dir <- rotacaoDireita(y)
        3. retorna rotacaoEsquerda(p)
        """
        y = p.dir                                         # 1
        p.dir = self._rotacao_direita(y)                  # 2
        return self._rotacao_esquerda(p)                  # 3

    def _registrar(self, tipo, p):
        self.rotacoes[tipo] += 1
        self.historico_rotacoes.append((tipo, p.chave))

    # ============================================================ inserção
    def inserir(self, chave, valor=None):
        """
        Insere a chave. Devolve True se inseriu, False se a chave JÁ EXISTIA.
        No solver: False significa "estado já visitado, não expanda de novo".
        Complexidade: O(log n).
        """
        self._inseriu = False
        self.raiz = self._insere(self.raiz, chave, valor)
        if self._inseriu:
            self.quantidade += 1
        return self._inseriu

    def _insere(self, r, chave, valor):
        """
        insere (r, x)                                  [Aula 08, slides 20-21]
        Recursiva: o caso-base é a árvore vazia (linha 1).
        """
        # 1-3: caso-base — achou o lugar vazio: o novo nó vira esta subárvore
        if r is None:
            self._inseriu = True
            return NoAVL(chave, valor)

        # [acréscimo da equipe] chave igual = já existe; nada muda
        if chave == r.chave:
            return r

        if chave < r.chave:                                   # 4: vai para a esquerda
            r.esq = self._insere(r.esq, chave, valor)         # 5: chamada recursiva
            if altura(r.esq) - altura(r.dir) == 2:            # 6: desbalanceou (FB=+2)
                if chave < r.esq.chave:                       # 7: esq + esq = "reta"
                    self._registrar("RD", r)
                    r = self._rotacao_direita(r)              # 8
                else:                                         # 9: esq + dir = "curva"
                    self._registrar("RED", r)
                    r = self._rotacao_esquerda_direita(r)     # 10
        else:                                                 # 11: vai para a direita
            r.dir = self._insere(r.dir, chave, valor)         # 12
            if altura(r.esq) - altura(r.dir) == -2:           # 13: desbalanceou (FB=-2)
                if chave > r.dir.chave:                       # 14: dir + dir = "reta"
                    self._registrar("RE", r)
                    r = self._rotacao_esquerda(r)             # 15
                else:                                         # 16: dir + esq = "curva"
                    self._registrar("RDE", r)
                    r = self._rotacao_direita_esquerda(r)     # 17

        r.h = max(altura(r.esq), altura(r.dir)) + 1           # 18: atualiza a altura
        return r                                              # 19

    # ============================================================ busca
    def buscar(self, chave):
        """
        Pesquisa na árvore binária de busca (aula 07): em cada nó, decide
        esquerda ou direita, descartando metade da árvore.
        Devolve (encontrou, valor, comparações).  O(log n) na AVL.
        """
        r, comparacoes = self.raiz, 0
        while r is not None:
            comparacoes += 1
            if chave == r.chave:
                return True, r.valor, comparacoes
            r = r.esq if chave < r.chave else r.dir
        return False, None, comparacoes

    def contem(self, chave):
        return self.buscar(chave)[0]

    # ============================================================ consultas
    def altura(self):
        return altura(self.raiz)

    def em_ordem(self):
        """Percurso in-ordem (aula 07): devolve as chaves em ordem crescente."""
        saida = []

        def visita(r):
            if r is None:          # caso-base
                return
            visita(r.esq)
            saida.append(r.chave)
            visita(r.dir)

        visita(self.raiz)
        return saida

    def eh_avl(self):
        """Confere, nó a nó, se |FB| <= 1 e se as alturas guardadas estão certas."""
        def confere(r):
            if r is None:
                return True, -1
            ok_e, he = confere(r.esq)
            ok_d, hd = confere(r.dir)
            h = max(he, hd) + 1
            return ok_e and ok_d and abs(he - hd) <= 1 and r.h == h, h
        return confere(self.raiz)[0]

    def desenhar(self, rotulo=str):
        """
        Desenho em texto, com altura e FB de cada nó. Exemplo:
            50  (h=3, FB=-1)
            ├─E─ 25  (h=2, FB=-1)
            │   ├─E─ 15  (h=0, FB=0)
            ...
        """
        if self.raiz is None:
            return "(árvore vazia)"
        linhas = []

        def desenha(r, prefixo, lado, ultimo):
            if r is None:
                return
            conector = "" if lado == "" else ("└─" if ultimo else "├─") + lado + "─ "
            linhas.append(f"{prefixo}{conector}{rotulo(r.chave)}  (h={r.h}, FB={fator_balanceamento(r):+d})".replace("FB=+0", "FB=0"))
            novo = prefixo + ("" if lado == "" else ("    " if ultimo else "│   "))
            filhos = [(f, l) for f, l in ((r.esq, "E"), (r.dir, "D")) if f is not None]
            for i, (f, l) in enumerate(filhos):
                desenha(f, novo, l, i == len(filhos) - 1)

        desenha(self.raiz, "", "", True)
        return "\n".join(linhas)

    def __len__(self):
        return self.quantidade
