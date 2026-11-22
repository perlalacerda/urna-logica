"""
ALGORITMOS GULOSOS NO MAPA COM CUSTOS                    [Aula 11]

Algoritmo guloso genérico (aula 11, slide 5):
    algoritmoGuloso (C)               // C é o conjunto de candidatos
    1.  S <- {}                       // S é o conjunto que conterá a solução
    2.  enquanto (C != ∅ e não solução(S)) faça
    3.      x <- seleciona(C)         // C costuma ser uma fila de prioridade
    4.      C <- C - {x}
    5.      se (viável(S ∪ {x})) então    // faz escolha gulosa
    6.          S <- S ∪ {x}
    7.  se (solução(S)) então
    8.      retorna S
    9.  senão
    10.     retorna "Não existe solução"
Ele escolhe o que parece melhor AGORA e nunca volta atrás. Às vezes isso dá a
resposta ótima (troco com moedas 1, 2, 5); às vezes não (troco de 8 com moedas
1, 4, 6: o guloso dá 6+1+1, três moedas; o ótimo é 4+4, duas).

Este módulo tem três funções:

1. dijkstra(G, s)            — o Dijkstra da aula 11, LINHA A LINHA, no grafo
                               puro (sem pistas nem portas). Guloso que DÁ CERTO.
2. dijkstra_estados(problema)— o mesmo Dijkstra no ESPAÇO DE ESTADOS do jogo
                               (posição + pistas + portas), respeitando as regras.
3. guloso_ingenuo(problema)  — "vá sempre pelo corredor mais barato": guloso
                               que NÃO dá certo, para comparar.

Por que o Dijkstra é guloso e funciona?
    A cada passo ele escolhe (Extrai-Min) o vértice com a MENOR distância
    estimada d[u] e a dá como definitiva (S <- S ∪ {u}). Com pesos NÃO
    negativos, nenhum caminho que ainda falta examinar pode ficar mais barato
    que d[u], porque somar pesos >= 0 nunca diminui o custo. Por isso a escolha
    gulosa é segura. O "vizinho mais barato" escolhe só o PRÓXIMO corredor, sem
    olhar o custo total desde a origem — e por isso pode errar.

BFS × Dijkstra (pergunta do item 7.2 do EP)
    BFS acha o caminho com MENOS ARESTAS (menos movimentos). Isso só é o caminho
    de MENOR CUSTO quando todas as arestas custam o mesmo. Com pesos diferentes,
    é preciso Dijkstra. A aula 11 (slide 21) diz: o Dijkstra "pode ser visto como uma
    generalização da busca em largura (BFS)".
"""

import time

from estruturas.heap import HeapMinimo
from estruturas.avl import ArvoreAVL
from algoritmos.solver import Resultado

INFINITO = float("inf")


# ======================================================== 1. Dijkstra da aula
def inicializa(G, s):
    """
    inicializa (G, s)                                     [Aula 11, slide 22]
    1. para cada vértice v ∈ V[G] faça
    2.     d[v] <- ∞
    3.     π[v] <- NULL
    4. d[s] <- 0
    Complexidade: O(|V|).
    """
    d, pi = {}, {}
    for v in G.vertices():          # 1
        d[v] = INFINITO             # 2
        pi[v] = None                # 3
    d[s] = 0                        # 4
    return d, pi


def relaxa(u, v, w, d, pi):
    """
    relaxa (u, v, w)                                      [Aula 11, slides 23-24]
    1. se d[v] > d[u] + w(u, v) então
    2.     d[v] <- d[u] + w(u, v)
    3.     π[v] <- u
    Ex. da aula: d[u] = 5, w = 2, d[v] = 9  ->  d[v] passa a 7.
    Devolve True se melhorou a estimativa.
    """
    if d[v] > d[u] + w:             # 1
        d[v] = d[u] + w             # 2
        pi[v] = u                   # 3
        return True
    return False


def dijkstra(G, s):
    """
    Dijkstra (G, s)                                       [Aula 11, slide 25]
    1. inicializa (G, s)
    2. S <- ∅
    3. Q <- V[G]        //Fila de prioridade de mínimo, com vértices de G
    4. enquanto (Q != ∅) faça
    5.     u <- Extrai-Min (Q)
    6.     S <- S ∪ {u}
    7.     para cada vértice v ∈ Adj[u] faça
    8.         relaxa (u, v, w)
    Complexidade com heap binário: O((|V| + |E|) log |V|)        [slide 27]

    Devolve (d, π, S na ordem em que os vértices entraram, passos).
    'passos' guarda, para cada Extrai-Min, quem saiu e quais relaxamentos
    melhoraram alguma estimativa — é o que a tela mostra passo a passo.
    """
    d, pi = inicializa(G, s)                                   # 1
    S = []                                                     # 2
    Q = HeapMinimo()                                           # 3
    for v in G.vertices():
        Q.inserir(v, d[v])
    passos = []
    while not Q.esta_vazio():                                  # 4
        _, u, _ = Q.extrair_minimo()                           # 5
        S.append(u)                                            # 6
        melhorou = []
        for v in G.vizinhos(u):                                # 7
            # Se v já está em S, relaxa não muda nada: d[v] <= d[u] e w >= 0.
            # Por isso só quem ainda está no heap pode melhorar (diminuir_chave).
            antes = d[v]
            if relaxa(u, v, G.peso(u, v), d, pi):              # 8
                Q.diminuir_chave(v, d[v])                      # heap atualiza: O(log |V|)
                melhorou.append((v, antes, d[v]))
        passos.append({"extraiu": u, "d": d[u], "melhorou": melhorou, "heap": Q.itens()})
    return d, pi, S, passos


# ======================================================== 2. Dijkstra no espaço de estados
def dijkstra_estados(problema):
    """
    O MESMO Dijkstra, agora sobre o grafo IMPLÍCITO de estados do jogo.

    Vértice  = chave do estado: (posição, pistas, portas) — sem a energia.
    d[chave] = energia gasta para chegar nele (o custo do caminho).
    Energia restante = energia inicial - d. Por isso a energia não precisa
    fazer parte do vértice: o melhor jeito de chegar é o que gasta MENOS.

    Diferenças em relação à versão da aula (necessárias, não de método):
    - Q começa só com o estado inicial, e os estados entram no heap quando são
      descobertos (o grafo de estados não está pronto na memória: é gerado
      pelas regras, como no solver BFS/DFS).
    - S (os estados já definitivos) é guardado na AVL da Fase 4.
    - A busca para quando o estado-objetivo sai do heap: nesse momento d[objetivo]
      já é definitivo (mesmo argumento da escolha gulosa acima).
    - Um movimento só existe se a energia restante pagar o corredor: isso já é
      verificado pela função mover(), a MESMA usada pelo jogador.
    """
    r, inicio = Resultado("Dijkstra"), time.perf_counter()
    vertice = getattr(problema, "configuracao", problema.chave)   # energia = E - d: não entra no vértice
    s = problema.estado_inicial()
    k0 = vertice(s)
    d = {k0: 0}                    # d[] da aula
    pais = {k0: (None, None)}      # π[] da aula (com a ação que levou ao estado)
    estado_de = {k0: s}            # o estado completo guardado para cada vértice
    S = ArvoreAVL()                # estados definitivos
    Q = HeapMinimo()
    Q.inserir(k0, 0)
    objetivo = None
    while not Q.esta_vazio():
        _, k, dk = Q.extrair_minimo()                  # Extrai-Min: o mais barato
        S.inserir(k, dk)                               # S <- S ∪ {u}
        u = estado_de[k]
        r.expandidos += 1
        r.ordem.append(u)
        if problema.eh_objetivo(u):
            objetivo = k
            r.passos.append((u, [estado_de[x] for _, _, x in Q.heap[1:]]))
            break
        for acao, novo, w in problema.sucessores(u):
            r.gerados += 1
            kv = vertice(novo)
            achou, _, _ = S.buscar(kv)
            if achou:                                  # já definitivo
                r.repetidos += 1
                continue
            if kv not in d or d[kv] > dk + w:          # relaxa(u, v, w)
                d[kv] = dk + w
                pais[kv] = (k, acao)
                estado_de[kv] = novo
                if Q.contem(kv):
                    Q.diminuir_chave(kv, d[kv])
                else:
                    Q.inserir(kv, d[kv])
            else:
                r.repetidos += 1                       # caminho mais caro: descartado
        r.passos.append((u, [estado_de[x] for _, _, x in Q.heap[1:]]))
    r.maior_fronteira = Q.maior_tamanho
    for k, (pai, acao) in pais.items():                # árvore de caminhos mínimos (π)
        if pai is not None:
            r.arvore.append((estado_de[pai], acao, estado_de[k]))
    if objetivo is not None:
        r.encontrou = True
        caminho, k = [], objetivo
        while k is not None:
            pai, acao = pais[k]
            caminho.append((acao, estado_de[k]))
            k = pai
        r.caminho = list(reversed(caminho))
        r.custo = d[objetivo]
    r.avl_altura, r.avl_nos = S.altura(), len(S)
    r.avl_rotacoes = sum(S.rotacoes.values())
    r.tempo_ms = (time.perf_counter() - inicio) * 1000
    return r


# ======================================================== 3. guloso ingênuo
def guloso_ingenuo(problema):
    """
    "Vá sempre pelo corredor mais barato" — o algoritmo guloso genérico da
    aula 11 aplicado de forma ingênua:
        C        = os movimentos possíveis a partir de onde estou
        seleciona = o corredor de MENOR custo (Extrai-Min de um heap)
        viável    = o movimento obedece às regras e não volta a um estado
                    já visitado (senão andaria em círculos para sempre)
        solução   = chegar ao destino
    Nunca volta atrás. Se ficar sem movimento viável, para sem solução.
    O resultado é comparado com o Dijkstra: mesmo quando chega, pode gastar mais.
    """
    r, inicio = Resultado("Guloso (corredor mais barato)"), time.perf_counter()
    u = problema.estado_inicial()
    lugar = getattr(problema, "configuracao", problema.chave)     # "não voltar" = não repetir a configuração
    visitados = ArvoreAVL()
    visitados.inserir(lugar(u), problema.recurso(u))
    r.caminho = [(None, u)]
    r.ordem.append(u)
    r.expandidos = 1
    while not problema.eh_objetivo(u):                       # não solução(S)
        C = HeapMinimo()                                     # C: fila de prioridade
        for acao, novo, w in problema.sucessores(u):
            r.gerados += 1
            achou, _, _ = visitados.buscar(lugar(novo))
            if achou:                                        # não viável: repetiria estado
                r.repetidos += 1
                continue
            C.inserir((acao, novo), w)
        r.maior_fronteira = max(r.maior_fronteira, C.maior_tamanho)
        r.passos.append((u, [x for _, _, (_, x) in C.heap[1:]]))
        if C.esta_vazio():                                   # C = ∅: sem saída
            break
        _, (acao, novo), w = C.extrair_minimo()              # x <- seleciona(C)
        r.arvore.append((u, acao, novo))
        r.custo += w
        visitados.inserir(lugar(novo), problema.recurso(novo))
        r.caminho.append((acao, novo))                       # S <- S ∪ {x}
        r.ordem.append(novo)
        r.expandidos += 1
        u = novo
    r.encontrou = problema.eh_objetivo(u)
    r.avl_altura, r.avl_nos = visitados.altura(), len(visitados)
    r.avl_rotacoes = sum(visitados.rotacoes.values())
    r.tempo_ms = (time.perf_counter() - inicio) * 1000
    return r
