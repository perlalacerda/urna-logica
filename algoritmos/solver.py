"""
SOLVER — busca no ESPAÇO DE ESTADOS com BFS e DFS.

Ideia central (aula 09: "Muitas aplicações são abstraídas como problemas de
busca"): cada situação do jogo é um VÉRTICE e cada ação válida é uma ARESTA.
O grafo de estados não é guardado inteiro: os vizinhos de um estado são
gerados quando necessário (grafo IMPLÍCITO), pela função sucessores().

Um "problema" é qualquer objeto com:
    estado_inicial()       -> estado
    sucessores(estado)     -> [(acao, novo_estado, custo)]   (as MESMAS regras do jogador)
    eh_objetivo(estado)    -> True/False
    chave(estado)          -> chave comparável usada na AVL
    recurso(estado)        -> número (ex.: energia restante); 0 se não houver

CONTROLE DE ESTADOS VISITADOS (Fase 4 — AVL)
    Antes de explorar um estado, o solver pergunta à AVL: "já vi esta chave?"
    - Se não viu: insere e explora.
    - Se viu com recurso MAIOR OU IGUAL: é repetido -> NÃO expande de novo.
    - Se viu com recurso MENOR: o novo é melhor (mais energia) -> atualiza e explora.
    Essa regra de "dominância" é segura: chegar ao mesmo lugar, com as mesmas
    pistas e portas, porém com MENOS energia, nunca permite fazer algo novo.

BFS x DFS
    BFS usa FILA: explora por camadas (1 ação, depois 2, depois 3...).
        => a primeira solução encontrada tem o MENOR NÚMERO DE AÇÕES.
        Isso vale porque toda ação conta 1. NÃO garante menor custo se as
        ações tiverem pesos diferentes (para isso seria preciso Dijkstra).
    DFS usa PILHA (ou a pilha de chamadas, na versão recursiva): mergulha num
        caminho até o fim antes de voltar. Costuma guardar menos estados de
        uma vez, mas a solução encontrada pode ser mais longa.
"""

import time

from estruturas.fila import Fila
from estruturas.pilha import Pilha
from estruturas.avl import ArvoreAVL


class Resultado:
    """Tudo o que o EP pede para exibir (RF10 e seção 15.1)."""

    def __init__(self, algoritmo):
        self.algoritmo = algoritmo
        self.encontrou = False
        self.caminho = []             # [(acao, estado)], começando com (None, inicial)
        self.custo = 0
        self.expandidos = 0           # estados retirados da fila/pilha e explorados
        self.gerados = 0              # sucessores produzidos
        self.repetidos = 0            # sucessores descartados pela AVL
        self.maior_fronteira = 0      # tamanho máximo da fila / pilha / profundidade
        self.tempo_ms = 0.0
        self.ordem = []               # ordem em que os estados foram expandidos
        self.arvore = []              # arestas da árvore de busca: (pai, acao, filho)
        self.passos = []              # para animação: (estado expandido, fronteira naquele momento)
        self.avl_altura = -1
        self.avl_nos = 0
        self.avl_rotacoes = 0

    def numero_acoes(self):
        return max(0, len(self.caminho) - 1)

    def resumo(self):
        return (f"{self.algoritmo}: {'solução com ' + str(self.numero_acoes()) + ' ações' if self.encontrou else 'sem solução'}"
                f", custo {self.custo}, {self.expandidos} estados expandidos, {self.gerados} gerados, "
                f"{self.repetidos} repetidos ignorados, fronteira máx. {self.maior_fronteira}, "
                f"AVL: {self.avl_nos} nós / altura {self.avl_altura} / {self.avl_rotacoes} rotações, "
                f"{self.tempo_ms:.3f} ms")


class _Visitados:
    """Controle de visitados com AVL + dominância por recurso."""

    def __init__(self, problema):
        self.problema = problema
        self.avl = ArvoreAVL()

    def eh_repetido(self, estado):
        achou, melhor, _ = self.avl.buscar(self.problema.chave(estado))
        return achou and self.problema.recurso(estado) <= melhor

    def marcar(self, estado):
        chave, rec = self.problema.chave(estado), self.problema.recurso(estado)
        if not self.avl.inserir(chave, rec):
            self.avl.atualizar_valor(chave, rec)

    def preencher(self, r):
        r.avl_altura = self.avl.altura()
        r.avl_nos = len(self.avl)
        r.avl_rotacoes = sum(self.avl.rotacoes.values())


def _reconstruir(pais, objetivo):
    """Segue os pais do objetivo até o início (como o π da aula 09)."""
    caminho, e = [], objetivo
    while e is not None:
        pai, acao = pais[e]
        caminho.append((acao, e))
        e = pai
    caminho.reverse()
    return caminho


def _finalizar(r, problema, pais, objetivo, visitados, inicio):
    if objetivo is not None:
        r.encontrou = True
        r.caminho = _reconstruir(pais, objetivo)
        r.custo = sum(c for _, _, c in _custos(problema, r.caminho))
    visitados.preencher(r)
    r.tempo_ms = (time.perf_counter() - inicio) * 1000
    return r


def _custos(problema, caminho):
    """Recalcula o custo de cada ação do caminho (via sucessores)."""
    for (_, e1), (acao, e2) in zip(caminho, caminho[1:]):
        for a, novo, custo in problema.sucessores(e1):
            if a == acao and novo == e2:
                yield a, novo, custo
                break


# ==================================================================== BFS
def bfs(problema):
    """
    Mesma estrutura do BFS da aula 09, trocando "vértice" por "estado":
        Q <- ∅; enqueue(Q, s)
        enquanto Q != ∅:
            u <- dequeue(Q)
            se u é objetivo: pare
            para cada sucessor v de u:
                se v não é repetido: marque v; π[v] <- u; enqueue(Q, v)
    """
    r, inicio = Resultado("BFS"), time.perf_counter()
    visitados = _Visitados(problema)
    s = problema.estado_inicial()
    pais = {s: (None, None)}            # π: só para reconstruir o caminho
    visitados.marcar(s)
    Q = Fila()
    Q.enqueue(s)
    while not Q.esta_vazia():
        _, u = Q.dequeue()
        r.expandidos += 1
        r.ordem.append(u)
        if problema.eh_objetivo(u):
            r.passos.append((u, Q.para_lista()))
            r.maior_fronteira = Q.maior_tamanho
            return _finalizar(r, problema, pais, u, visitados, inicio)
        for acao, v, _ in problema.sucessores(u):
            r.gerados += 1
            if visitados.eh_repetido(v):
                r.repetidos += 1
                continue
            visitados.marcar(v)
            pais[v] = (u, acao)
            r.arvore.append((u, acao, v))
            Q.enqueue(v)
        r.passos.append((u, Q.para_lista()))
    r.maior_fronteira = Q.maior_tamanho
    return _finalizar(r, problema, pais, None, visitados, inicio)


# ==================================================================== DFS recursiva
def dfs_recursiva(problema):
    """
    Mesma estrutura do visitaDFS da aula 09:
        visita(u):
            CASO-BASE 1: u é objetivo        -> devolve "achei"
            para cada sucessor v de u:
                se v não é repetido:
                    marque v; π[v] <- u
                    CHAMADA RECURSIVA: visita(v)
                    se achou: devolve "achei" (CONDIÇÃO DE RETORNO)
            CASO-BASE 2: nenhum sucessor levou ao objetivo -> devolve "não achei"
    A "pilha" aqui é a pilha de chamadas do Python; medimos sua profundidade.
    """
    r, inicio = Resultado("DFS (recursiva)"), time.perf_counter()
    visitados = _Visitados(problema)
    s = problema.estado_inicial()
    pais = {s: (None, None)}
    visitados.marcar(s)

    chamadas = []                       # espelho da pilha de chamadas, só para animação

    def visita(u, profundidade):
        chamadas.append(u)
        r.expandidos += 1
        r.ordem.append(u)
        r.passos.append((u, list(reversed(chamadas))))
        r.maior_fronteira = max(r.maior_fronteira, profundidade)
        if problema.eh_objetivo(u):                       # caso-base 1
            return u
        for acao, v, _ in problema.sucessores(u):
            r.gerados += 1
            if visitados.eh_repetido(v):
                r.repetidos += 1
                continue
            visitados.marcar(v)
            pais[v] = (u, acao)
            r.arvore.append((u, acao, v))
            achado = visita(v, profundidade + 1)          # chamada recursiva
            if achado is not None:                        # condição de retorno
                return achado
        chamadas.pop()
        return None                                       # caso-base 2: beco sem saída

    objetivo = visita(s, 1)
    return _finalizar(r, problema, pais, objetivo, visitados, inicio)


# ==================================================================== DFS com pilha
def dfs_pilha(problema):
    """
    DFS iterativa: a pilha explícita substitui a recursão
    ("Simulação de recursão com pilha", aula 06).
        P <- ∅; push(P, s)
        enquanto P != ∅:
            u <- pop(P)
            se u é repetido: ignore
            marque u
            se u é objetivo: pare
            empilhe os sucessores (em ordem inversa, para visitar o 1º primeiro)
    """
    r, inicio = Resultado("DFS (pilha)"), time.perf_counter()
    visitados = _Visitados(problema)
    s = problema.estado_inicial()
    pais = {s: (None, None)}
    P = Pilha()
    P.push(s)
    while not P.esta_vazia():
        _, u = P.pop()
        if visitados.eh_repetido(u):
            r.repetidos += 1
            continue
        visitados.marcar(u)
        r.expandidos += 1
        r.ordem.append(u)
        if pais[u][0] is not None:
            r.arvore.append((pais[u][0], pais[u][1], u))
        if problema.eh_objetivo(u):
            r.passos.append((u, P.para_lista()))
            r.maior_fronteira = P.maior_tamanho
            return _finalizar(r, problema, pais, u, visitados, inicio)
        for acao, v, _ in reversed(problema.sucessores(u)):
            r.gerados += 1
            if visitados.eh_repetido(v):
                r.repetidos += 1
                continue
            pais[v] = (u, acao)
            P.push(v)
        r.passos.append((u, P.para_lista()))
    r.maior_fronteira = P.maior_tamanho
    return _finalizar(r, problema, pais, None, visitados, inicio)


ALGORITMOS_BUSCA = {"bfs": bfs, "dfs": dfs_recursiva, "dfs_pilha": dfs_pilha}


def desenhar_arvore_de_busca(resultado, rotulo, limite=60):
    """
    Árvore de busca em texto: cada nó é um estado, cada aresta é a ação que
    levou a ele (exigência do item 9.2). Mostra até 'limite' nós.
    """
    filhos = {}
    raiz = resultado.ordem[0] if resultado.ordem else None
    for pai, acao, filho in resultado.arvore:
        filhos.setdefault(pai, []).append((acao, filho))
    no_caminho = {e for _, e in resultado.caminho}
    linhas, contador = [], [0]

    def desenha(e, prefixo, conector):
        if contador[0] >= limite:
            return
        contador[0] += 1
        marca = "  <== caminho" if e in no_caminho else ""
        linhas.append(f"{prefixo}{conector}{rotulo(e)}{marca}")
        lista = filhos.get(e, [])
        for i, (acao, f) in enumerate(lista):
            ultimo = i == len(lista) - 1
            novo_prefixo = prefixo + ("" if conector == "" else ("    " if conector.startswith("└") else "│   "))
            desenha(f, novo_prefixo, ("└─" if ultimo else "├─") + f"[{acao}]─ ")

    if raiz is not None:
        desenha(raiz, "", "")
    if contador[0] >= limite:
        linhas.append(f"... (mostrando {limite} de {len(resultado.arvore) + 1} nós)")
    return "\n".join(linhas)
