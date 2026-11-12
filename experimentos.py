"""
Experimentos de desempenho para o relatório técnico (seção 15.1 do EP).

Rodar:   py experimentos.py          (Windows)
         python3 experimentos.py     (Linux/Mac)

Gera docs/metricas.md com:
  1. Ordenação: comparações, movimentações e tempo (mediana de 5 repetições)
     para vários tamanhos e para dados aleatórios, já ordenados e invertidos.
  2. Busca: BFS x DFS (recursiva e com pilha) em três cenários.
  3. AVL: altura x número de nós (comparação com log2 n).

Os TEMPOS dependem da máquina; comparações, movimentações e estados
explorados não dependem (são determinísticos para a mesma seed).
"""

import math
import platform
import statistics
import sys
import time

from algoritmos.ordenacao import ordenar
from algoritmos.solver import bfs, dfs_recursiva, dfs_pilha
from estruturas.avl import ArvoreAVL
from jogo.registros import gerar_registros, embaralhar, CRITERIOS
from jogo.cenarios import cenario_padrao, gerar_mapa

REPETICOES = 5
SEED = 2042


def medir_ordenacao():
    linhas = []
    chave = CRITERIOS["auditoria"]
    for n in (100, 500, 1000, 2000):
        base = embaralhar(gerar_registros(n, SEED), SEED + 1)
        entradas = {"aleatório": base,
                    "já ordenado": sorted(base, key=chave),
                    "invertido": sorted(base, key=chave, reverse=True)}
        for tipo, dados in entradas.items():
            if tipo != "aleatório" and n > 1000:
                continue          # quick sort no pior caso: recursão de profundidade n
            for alg in ("bubble", "merge", "quick"):
                tempos, ultimo = [], None
                for _ in range(REPETICOES):
                    A = list(dados)
                    ultimo = ordenar(A, alg, chave)
                    tempos.append(ultimo.tempo_ms)
                linhas.append((n, tipo, ultimo.algoritmo, ultimo.comparacoes,
                               ultimo.movimentacoes, statistics.median(tempos)))
    return linhas


def medir_busca():
    cenarios = [("mapa padrão (9 vértices, 11 arestas)", cenario_padrao())]
    for n in (30, 60):
        p, s = gerar_mapa(SEED, n=n)
        cenarios.append((f"mapa gerado ({n} vértices, {p.G.numero_arestas()} arestas, seed {s})", p))
    linhas = []
    for nome, p in cenarios:
        for alg in (bfs, dfs_recursiva, dfs_pilha):
            tempos, r = [], None
            for _ in range(REPETICOES):
                r = alg(p)
                tempos.append(r.tempo_ms)
            linhas.append((nome, r.algoritmo, r.numero_acoes() if r.encontrou else "-",
                           r.expandidos, r.gerados, r.repetidos, r.maior_fronteira,
                           r.avl_nos, r.avl_altura, r.avl_rotacoes, statistics.median(tempos)))
    return linhas


def medir_avl():
    linhas = []
    for n in (15, 100, 1000, 10000):
        a = ArvoreAVL()
        t0 = time.perf_counter()
        for k in range(n):                  # inserção EM ORDEM: pior caso de uma BST comum
            a.inserir(k)
        ms = (time.perf_counter() - t0) * 1000
        linhas.append((n, a.altura(), math.log2(n), sum(a.rotacoes.values()), ms))
    return linhas


def main():
    sys.setrecursionlimit(10000)
    L = ["# Métricas de desempenho — Urna Lógica", "",
         f"Gerado por `experimentos.py`. Ambiente: Python {sys.version.split()[0]}, "
         f"{platform.system()} {platform.release()}, processador `{platform.processor() or platform.machine()}`.",
         f"Seed {SEED}; tempos = mediana de {REPETICOES} repetições, em milissegundos.",
         "Tempos variam entre máquinas; contagens não variam.", "",
         "## 1. Ordenação (chave composta zona → seção → horário → id)", "",
         "| n | entrada | algoritmo | comparações | movimentações | tempo (ms) |",
         "|---:|---|---|---:|---:|---:|"]
    for n, tipo, alg, comp, mov, ms in medir_ordenacao():
        L.append(f"| {n} | {tipo} | {alg} | {comp} | {mov} | {ms:.3f} |")
    L += ["", "Referência teórica (aulas 03 e 04): Bubble faz sempre n(n−1)/2 comparações, Θ(n²); "
          "Merge, Θ(n log n) em todos os casos; Quick, Θ(n log n) no caso médio e Θ(n²) com entrada "
          "já ordenada ou invertida (pivô = último elemento).", "",
          "## 2. Busca no espaço de estados (Fase 3)", "",
          "| cenário | estratégia | ações | expandidos | gerados | repetidos | fronteira máx. | nós AVL | altura AVL | rotações | tempo (ms) |",
          "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for linha in medir_busca():
        *campos, ms = linha
        L.append("| " + " | ".join(str(c) for c in campos) + f" | {ms:.3f} |")
    L += ["", "BFS encontra o menor número de ações porque cada ação custa 1. A DFS não tem essa garantia: "
          "a rota encontrada tende a ser mais longa, e o número de estados expandidos pode ser menor ou "
          "maior que o da BFS, conforme a ordem dos vizinhos e a posição do objetivo. Complexidade: O(|V| + |E|) no grafo de "
          "estados, cujo tamanho cresce com o número de combinações de posição, pistas e portas.", "",
          "## 3. Árvore AVL — altura × número de nós", "",
          "| nós | altura | log2(n) | rotações | tempo total de inserção (ms) |",
          "|---:|---:|---:|---:|---:|"]
    for n, h, lg, rot, ms in medir_avl():
        L.append(f"| {n} | {h} | {lg:.2f} | {rot} | {ms:.3f} |")
    L += ["", "Inserindo chaves em ordem crescente, uma árvore binária de busca comum degeneraria em lista "
          "(altura n − 1). A AVL mantém a altura próxima de log2(n), por isso busca e inserção custam "
          "O(log n) (aula 08)."]
    with open("docs/metricas.md", "w", encoding="utf-8") as arq:
        arq.write("\n".join(L) + "\n")
    print("\n".join(L))
    print("\nGravado em docs/metricas.md")


if __name__ == "__main__":
    main()
