"""
Nó (ou elemento) de uma estrutura ligada.        [Aula 06, slide 7]

    +-------+------+
    | chave | prox | --->  próximo nó (ou None, que faz o papel de NULL)
    +-------+------+

Usado pela lista ligada, pela pilha dinâmica e pela fila dinâmica.
"""


class No:
    def __init__(self, chave):
        self.chave = chave   # o conteúdo guardado (evidência, estado, etc.)
        self.prox = None     # referência para o sucessor; None = NULL

    def __repr__(self):
        return f"No({self.chave!r})"
