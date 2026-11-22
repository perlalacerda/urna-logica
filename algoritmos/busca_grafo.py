"""
BFS e DFS sobre um grafo explícito — exatamente como na aula 09.

Cores (aula 09):
    BRANCO = ainda não descoberto
    CINZA  = descoberto, mas ainda com vizinhos por examinar
    PRETO  = todos os vizinhos já examinados

Saídas:
    d[v]  BFS: distância (em número de arestas) de s até v
          DFS: momento de descoberta
    f[v]  DFS: momento de finalização
    π[v]  pai de v na árvore de busca (pi)
"""

from estruturas.fila import Fila

BRANCO, CINZA, PRETO = "BRANCO", "CINZA", "PRETO"
INFINITO = float("inf")


def bfs(G, s):
    """
    BFS (G, s)                                         [Aula 09, slides 71-72]
    1. cor[s] <- CINZA; d[s] <- 0; π[s] <- NULL
    4. para cada u em V[G]-{s}: cor[u] <- BRANCO; d[u] <- ∞; π[u] <- NULL
    8. Q <- ∅
    9. enqueue(Q, s)
    10. enquanto Q != ∅ faça
    11.    u <- dequeue(Q)
    12.    para cada v em Adj[u]
    13.        se cor[v] = BRANCO então
    14.            cor[v] <- CINZA
    15.            d[v] <- d[u] + 1
    16.            π[v] <- u
    17.            enqueue(Q, v)
    18.    cor[u] <- PRETO
    Complexidade: O(|V| + |E|).
    Devolve (d, pi, ordem_de_visita, maior_tamanho_da_fila).
    """
    cor, d, pi = {}, {}, {}
    for u in G.vertices():                          # 4-7
        cor[u], d[u], pi[u] = BRANCO, INFINITO, None
    cor[s], d[s], pi[s] = CINZA, 0, None            # 1-3
    Q = Fila()                                      # 8
    Q.enqueue(s)                                    # 9
    ordem = []
    while not Q.esta_vazia():                       # 10
        _, u = Q.dequeue()                          # 11
        ordem.append(u)
        for v in G.vizinhos(u):                     # 12
            if cor[v] == BRANCO:                    # 13
                cor[v] = CINZA                      # 14
                d[v] = d[u] + 1                     # 15
                pi[v] = u                           # 16
                Q.enqueue(v)                        # 17
        cor[u] = PRETO                              # 18
    return d, pi, ordem, Q.maior_tamanho


def dfs(G, ordem_vertices=None):
    """
    DFS (G)                                            [Aula 09, slides 54-55]
    1. para cada u em V[G]: cor[u] <- BRANCO; π[u] <- NULL
    4. tempo <- 0
    5. para cada u em V[G]
    6.     se cor[u] = BRANCO então visitaDFS(u)
    Complexidade: O(|V| + |E|).
    Devolve (d, f, pi, ordem_de_descoberta).
    ordem_vertices: a ordem de V[G] nas linhas 1 e 5 (padrão: alfabética).
    O exemplo dos slides 29-52 percorre V[G] começando por s.
    """
    V = list(ordem_vertices) if ordem_vertices is not None else G.vertices()
    cor, d, f, pi = {}, {}, {}, {}
    for u in V:                                     # 1-3
        cor[u], pi[u] = BRANCO, None
    tempo = [0]                                     # 4 (lista: para alterar dentro da função)
    ordem = []

    def visita_dfs(u):
        """
        visitaDFS (u)  — RECURSIVA                     [Aula 09, slide 55]
        1. cor[u] <- CINZA            // u foi descoberto
        2. tempo <- tempo + 1
        3. d[u] <- tempo
        4. para cada v em Adj[u]
        5.     se cor[v] = BRANCO então
        6.         π[v] <- u
        7.         visitaDFS(v)       // chamada recursiva
        8. cor[u] <- PRETO            // visitou todos os vizinhos de u
        9. tempo <- tempo + 1
        10. f[u] <- tempo
        Caso-base implícito: quando nenhum vizinho é BRANCO, o laço não
        faz chamadas e a função retorna.
        """
        cor[u] = CINZA                              # 1
        tempo[0] += 1                               # 2
        d[u] = tempo[0]                             # 3
        ordem.append(u)
        for v in G.vizinhos(u):                     # 4
            if cor[v] == BRANCO:                    # 5
                pi[v] = u                           # 6
                visita_dfs(v)                       # 7
        cor[u] = PRETO                              # 8
        tempo[0] += 1                               # 9
        f[u] = tempo[0]                             # 10

    for u in V:                          # 5
        if cor[u] == BRANCO:                        # 6
            visita_dfs(u)                           # 7
    return d, f, pi, ordem


def caminho(pi, s, v):
    """Reconstrói o caminho s -> v seguindo os pais π (de trás para a frente)."""
    if v not in pi:
        return []
    seq = []
    while v is not None:
        seq.append(v)
        if v == s:
            return list(reversed(seq))
        v = pi[v]
    return []        # v não é alcançável a partir de s
