"""
Grafo representado por LISTA DE ADJACÊNCIA.        [Aula 09, slides 21-25]

"Uma lista de adjacência de um grafo com n vértices consiste de um vetor
 (ou arranjo) de n listas ligadas, uma para cada vértice no grafo."

    A -> B -> C
    B -> A -> C -> H -> I          cada linha é uma ListaLigada (aula 06)
    C -> A -> B -> E -> G
    ...

Por que lista e não matriz de adjacência?                  [Aula 09, slide 25]
    O mapa é ESPARSO: 9 vértices e 11 arestas, enquanto a matriz teria
    9 x 9 = 81 células, a maioria zero. Com lista, percorrer os vizinhos de u
    custa O(grau(u)), e BFS/DFS custam O(|V| + |E|).

Grafo não orientado: cada aresta {u, v} entra nas duas listas (u->v e v->u),
porque os corredores do mapa podem ser percorridos nos dois sentidos.
"""

from estruturas.lista_ligada import ListaLigada


class Grafo:
    def __init__(self, orientado=False):
        self.orientado = orientado
        self.adj = {}          # "vetor" indexado pelo nome do vértice -> ListaLigada
        self.nomes = {}        # rótulo legível de cada vértice

    def adicionar_vertice(self, v, nome=""):
        if v not in self.adj:
            self.adj[v] = ListaLigada()
            self.nomes[v] = nome or v

    def adicionar_aresta(self, u, v):
        """
        Insere a aresta (u, v). Vizinhos repetidos são ignorados, para que
        a mesma conexão não apareça duas vezes na lista (caso de teste do EP).
        Mantém cada lista em ordem alfabética: assim a ordem de visita da
        BFS/DFS é sempre a mesma (reprodutível) e fácil de conferir à mão.
        """
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        self._inserir_ordenado(u, v)
        if not self.orientado:
            self._inserir_ordenado(v, u)

    def _inserir_ordenado(self, u, v):
        lista = self.adj[u]
        if lista.contem(v):
            return
        anterior = None
        for w in lista.percorrer():
            if w < v:
                anterior = w
        if anterior is None:
            lista.inserir_inicio(v)
        else:
            lista.inserir_apos(anterior, v)

    def vizinhos(self, u):
        """Adj[u] da aula: os vértices v tais que existe a aresta (u, v)."""
        return self.adj[u].percorrer() if u in self.adj else []

    def existe_aresta(self, u, v):
        return u in self.adj and self.adj[u].contem(v)

    def vertices(self):
        return sorted(self.adj)

    def numero_arestas(self):
        total = sum(len(lista) for lista in self.adj.values())
        return total if self.orientado else total // 2

    def grau(self, u):
        return len(self.adj[u])

    def __str__(self):
        return "\n".join(f"  {u} ({self.nomes[u]}) -> " + (" -> ".join(self.vizinhos(u)) or "NULL")
                         for u in self.vertices())
