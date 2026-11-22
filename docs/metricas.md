# Métricas de desempenho — Urna Lógica

Gerado por `experimentos.py`. Ambiente: Python 3.13.18, Linux 6.18.44-fc-v726, processador `x86_64`.
Seed 2042; tempos = mediana de 5 repetições, em milissegundos.
Tempos variam entre máquinas; contagens não variam.

## 1. Ordenação (chave composta zona → seção → horário → id)

| n | entrada | algoritmo | comparações | movimentações | tempo (ms) |
|---:|---|---|---:|---:|---:|
| 100 | aleatório | Bubble Sort | 4950 | 6699 | 1.025 |
| 100 | aleatório | Merge Sort | 672 | 1344 | 0.222 |
| 100 | aleatório | Quick Sort | 697 | 1518 | 0.117 |
| 100 | já ordenado | Bubble Sort | 4950 | 0 | 0.910 |
| 100 | já ordenado | Merge Sort | 672 | 1344 | 0.235 |
| 100 | já ordenado | Quick Sort | 4950 | 15147 | 0.755 |
| 100 | invertido | Bubble Sort | 4950 | 14850 | 1.115 |
| 100 | invertido | Merge Sort | 672 | 1344 | 0.206 |
| 100 | invertido | Quick Sort | 4950 | 7647 | 0.678 |
| 500 | aleatório | Bubble Sort | 124750 | 183501 | 26.689 |
| 500 | aleatório | Merge Sort | 4488 | 8976 | 1.485 |
| 500 | aleatório | Quick Sort | 5994 | 10407 | 0.984 |
| 500 | já ordenado | Bubble Sort | 124750 | 0 | 32.115 |
| 500 | já ordenado | Merge Sort | 4488 | 8976 | 2.185 |
| 500 | já ordenado | Quick Sort | 124750 | 375747 | 20.891 |
| 500 | invertido | Bubble Sort | 124750 | 374250 | 26.479 |
| 500 | invertido | Merge Sort | 4488 | 8976 | 1.434 |
| 500 | invertido | Quick Sort | 124750 | 188247 | 16.442 |
| 1000 | aleatório | Bubble Sort | 499500 | 745314 | 103.428 |
| 1000 | aleatório | Merge Sort | 9976 | 19952 | 3.543 |
| 1000 | aleatório | Quick Sort | 10548 | 18642 | 2.399 |
| 1000 | já ordenado | Bubble Sort | 499500 | 0 | 85.858 |
| 1000 | já ordenado | Merge Sort | 9976 | 19952 | 3.291 |
| 1000 | já ordenado | Quick Sort | 499500 | 1501497 | 100.523 |
| 1000 | invertido | Bubble Sort | 499500 | 1498500 | 159.126 |
| 1000 | invertido | Merge Sort | 9976 | 19952 | 3.358 |
| 1000 | invertido | Quick Sort | 499500 | 751497 | 66.464 |
| 2000 | aleatório | Bubble Sort | 1999000 | 3008925 | 438.082 |
| 2000 | aleatório | Merge Sort | 21952 | 43904 | 10.114 |
| 2000 | aleatório | Quick Sort | 24250 | 38286 | 3.918 |

Referência teórica (aulas 03 e 04): Bubble faz sempre n(n−1)/2 comparações, Θ(n²); Merge, Θ(n log n) em todos os casos; Quick, Θ(n log n) no caso médio e Θ(n²) com entrada já ordenada ou invertida, ou com muitas chaves iguais (pivô = último elemento). As movimentações do Quick contam também as autotrocas A[i]↔A[i] da linha 6 do slide 32.

## 2. Busca no espaço de estados (Fase 3)

Chave da AVL = estado inteiro (posição, pistas, portas, energia), como pede o enunciado 8.1. As linhas “+ dominância” usam a melhoria opcional da equipe: descartam também a mesma configuração com energia menor ou igual (coluna “dominados”).

| cenário | estratégia | ações | expandidos | gerados | repetidos | dominados | fronteira máx. | nós AVL | altura AVL | rotações | tempo (ms) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mapa padrão (9 vértices, 11 arestas) | BFS | 7 | 70 | 177 | 86 | 0 | 24 | 92 | 7 | 49 | 0.817 |
| mapa padrão (9 vértices, 11 arestas) | DFS (recursiva) | 10 | 69 | 122 | 54 | 0 | 11 | 69 | 6 | 36 | 0.607 |
| mapa padrão (9 vértices, 11 arestas) | DFS (pilha) | 10 | 69 | 132 | 55 | 0 | 16 | 69 | 6 | 36 | 0.685 |
| mapa padrão (9 vértices, 11 arestas) | BFS + dominância | 7 | 18 | 44 | 24 | 22 | 5 | 21 | 4 | 9 | 0.233 |
| mapa padrão (9 vértices, 11 arestas) | DFS (recursiva) + dominância | 9 | 17 | 27 | 11 | 10 | 11 | 17 | 4 | 7 | 0.199 |
| mapa padrão (9 vértices, 11 arestas) | DFS (pilha) + dominância | 9 | 17 | 36 | 13 | 12 | 10 | 17 | 4 | 7 | 0.229 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | BFS | 7 | 149 | 446 | 201 | 0 | 99 | 246 | 8 | 124 | 3.163 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | DFS (recursiva) | 59 | 205 | 314 | 110 | 0 | 61 | 205 | 8 | 126 | 2.622 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | DFS (pilha) | 59 | 205 | 479 | 111 | 0 | 181 | 205 | 8 | 126 | 3.588 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | BFS + dominância | 7 | 59 | 171 | 86 | 70 | 29 | 86 | 6 | 42 | 1.015 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | DFS (recursiva) + dominância | 35 | 36 | 55 | 20 | 20 | 36 | 36 | 6 | 15 | 0.962 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | DFS (pilha) + dominância | 35 | 36 | 130 | 38 | 38 | 58 | 36 | 6 | 15 | 0.989 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | BFS | 8 | 704 | 2222 | 1294 | 0 | 231 | 929 | 11 | 495 | 16.889 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | DFS (recursiva) | 120 | 763 | 1606 | 844 | 0 | 121 | 763 | 10 | 406 | 14.234 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | DFS (pilha) | 120 | 763 | 2121 | 847 | 0 | 541 | 763 | 10 | 406 | 41.043 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | BFS + dominância | 8 | 181 | 556 | 339 | 302 | 38 | 218 | 8 | 86 | 5.459 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | DFS (recursiva) + dominância | 44 | 235 | 604 | 370 | 294 | 63 | 235 | 9 | 124 | 6.237 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | DFS (pilha) + dominância | 44 | 235 | 709 | 389 | 313 | 104 | 235 | 9 | 124 | 7.027 |

BFS encontra o menor número de ações porque cada ação custa 1. A DFS não tem essa garantia: a rota encontrada tende a ser mais longa, e o número de estados expandidos pode ser menor ou maior que o da BFS, conforme a ordem dos vizinhos e a posição do objetivo. Com a chave literal, nenhuma chave é expandida duas vezes. A dominância não muda o mínimo da BFS e reduz os expandidos. Complexidade: O((|V| + |E|) log |V|) no grafo de estados, porque cada sucessor é procurado na AVL; o grafo cresce com as combinações de posição, pistas e portas.

## 3. Árvore AVL — altura × número de nós

| nós | altura | log2(n) | rotações | tempo total de inserção (ms) |
|---:|---:|---:|---:|---:|
| 15 | 3 | 3.91 | 11 | 0.024 |
| 100 | 6 | 6.64 | 93 | 0.185 |
| 1000 | 9 | 9.97 | 990 | 2.918 |
| 10000 | 13 | 13.29 | 9986 | 39.439 |

Inserindo chaves em ordem crescente, uma árvore binária de busca comum degeneraria em lista (altura n − 1). A AVL mantém a altura próxima de log2(n), por isso busca e inserção custam O(log n) (aula 08).
