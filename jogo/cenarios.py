"""
Cenários para comparar BFS e DFS (seção 9.1: "pelo menos dois cenários de
tamanho ou dificuldade diferentes") e GERADOR DE MAPAS por seed (bônus).

Cenário 1 — mapa padrão da Fase 3 (9 vértices, 11 arestas, 2 portas).
Cenário 2 — mapa gerado por seed (padrão: 30 vértices), com as mesmas regras.

Como o gerador garante um mapa conexo e com solução?
    1. Sorteia uma ÁRVORE GERADORA: cada novo vértice se liga a um vértice já
       existente. Uma árvore com n vértices tem n-1 arestas e é conexa.
    2. Acrescenta arestas extras ao acaso (criam ciclos e rotas alternativas).
    3. Sorteia onde ficam as pistas SEQ e AUT e a porta que exige SEQ;
       o destino sempre exige AUT.
    4. VERIFICADOR AUTOMÁTICO: roda a BFS. Se não houver solução, tenta a
       próxima seed. Assim todo mapa entregue tem ao menos uma solução.
Tudo usa random.Random(seed): a mesma seed gera sempre o mesmo mapa.
"""

import random

from estruturas.grafo import Grafo
from jogo.fase3 import ProblemaMapa, construir_mapa
from algoritmos.solver import bfs


def gerar_mapa(seed, n=30, extras=None, energia=None, tentativas=50):
    """
    Devolve (problema, seed_usada). O problema já é um ProblemaMapa pronto
    para o solver. 'extras' = arestas além da árvore (padrão: n // 2).
    """
    extras = n // 2 if extras is None else extras
    for k in range(tentativas):
        s = seed + k
        rng = random.Random(s)
        nomes = [f"U{i:02d}" for i in range(1, n + 1)]
        G = Grafo()
        for v in nomes:
            G.adicionar_vertice(v, f"Unidade {v[1:]}")
        for i in range(1, n):                                   # 1. árvore geradora
            G.adicionar_aresta(nomes[i], nomes[rng.randrange(i)])
        while G.numero_arestas() < (n - 1) + extras:            # 2. arestas extras
            u, v = rng.sample(nomes, 2)
            G.adicionar_aresta(u, v)
        inicio, destino = nomes[0], nomes[-1]
        seq, aut, porta = rng.sample(nomes[1:-1], 3)            # 3. pistas e porta
        problema = ProblemaMapa(G=G, energia=energia or 2 * n, destino=destino, inicio=inicio,
                                pistas={seq: "SEQ", aut: "AUT"},
                                portas={porta: "SEQ", destino: "AUT"})
        if bfs(problema).encontrou:                             # 4. verificador
            return problema, s
    raise RuntimeError("Nenhum mapa com solução nas seeds testadas.")


def cenario_padrao():
    return ProblemaMapa(G=construir_mapa())


def cenarios_de_comparacao(seed=2042):
    """Os dois cenários usados no relatório da Fase 5."""
    grande, seed_usada = gerar_mapa(seed, n=30)
    return [("Cenário 1 — mapa padrão (9 vértices)", cenario_padrao()),
            (f"Cenário 2 — mapa gerado (30 vértices, seed {seed_usada})", grande)]
