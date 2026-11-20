# Métricas de desempenho — Urna Lógica

Gerado por `experimentos.py`. Ambiente: Python 3.13.18, Linux 6.18.44-fc-v726, processador `x86_64`.
Seed 2042; tempos = mediana de 5 repetições, em milissegundos.
Tempos variam entre máquinas; contagens não variam.

## 1. Ordenação (chave composta zona → seção → horário → id)

| n | entrada | algoritmo | comparações | movimentações | tempo (ms) |
|---:|---|---|---:|---:|---:|
| 100 | aleatório | Bubble Sort | 4950 | 6699 | 0.818 |
| 100 | aleatório | Merge Sort | 672 | 1344 | 0.192 |
| 100 | aleatório | Quick Sort | 697 | 1518 | 0.097 |
| 100 | já ordenado | Bubble Sort | 4950 | 0 | 0.671 |
| 100 | já ordenado | Merge Sort | 672 | 1344 | 0.166 |
| 100 | já ordenado | Quick Sort | 4950 | 15147 | 0.610 |
| 100 | invertido | Bubble Sort | 4950 | 14850 | 0.843 |
| 100 | invertido | Merge Sort | 672 | 1344 | 0.172 |
| 100 | invertido | Quick Sort | 4950 | 7647 | 0.544 |
| 500 | aleatório | Bubble Sort | 124750 | 183501 | 21.212 |
| 500 | aleatório | Merge Sort | 4488 | 8976 | 1.216 |
| 500 | aleatório | Quick Sort | 5994 | 10407 | 1.059 |
| 500 | já ordenado | Bubble Sort | 124750 | 0 | 18.080 |
| 500 | já ordenado | Merge Sort | 4488 | 8976 | 1.760 |
| 500 | já ordenado | Quick Sort | 124750 | 375747 | 24.578 |
| 500 | invertido | Bubble Sort | 124750 | 374250 | 21.970 |
| 500 | invertido | Merge Sort | 4488 | 8976 | 1.190 |
| 500 | invertido | Quick Sort | 124750 | 188247 | 13.549 |
| 1000 | aleatório | Bubble Sort | 499500 | 745314 | 86.978 |
| 1000 | aleatório | Merge Sort | 9976 | 19952 | 2.671 |
| 1000 | aleatório | Quick Sort | 10548 | 18642 | 1.441 |
| 1000 | já ordenado | Bubble Sort | 499500 | 0 | 72.451 |
| 1000 | já ordenado | Merge Sort | 9976 | 19952 | 2.740 |
| 1000 | já ordenado | Quick Sort | 499500 | 1501497 | 64.855 |
| 1000 | invertido | Bubble Sort | 499500 | 1498500 | 90.289 |
| 1000 | invertido | Merge Sort | 9976 | 19952 | 2.723 |
| 1000 | invertido | Quick Sort | 499500 | 751497 | 55.210 |
| 2000 | aleatório | Bubble Sort | 1999000 | 3008925 | 377.613 |
| 2000 | aleatório | Merge Sort | 21952 | 43904 | 6.155 |
| 2000 | aleatório | Quick Sort | 24250 | 38286 | 3.584 |

Referência teórica (aulas 03 e 04): Bubble faz sempre n(n−1)/2 comparações, Θ(n²); Merge, Θ(n log n) em todos os casos; Quick, Θ(n log n) no caso médio e Θ(n²) com entrada já ordenada ou invertida (pivô = último elemento).

## 2. Busca no espaço de estados (Fase 3)

| cenário | estratégia | ações | expandidos | gerados | repetidos | fronteira máx. | nós AVL | altura AVL | rotações | tempo (ms) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mapa padrão (9 vértices, 11 arestas) | BFS | 7 | 18 | 44 | 24 | 5 | 21 | 4 | 9 | 0.191 |
| mapa padrão (9 vértices, 11 arestas) | DFS (recursiva) | 9 | 17 | 27 | 11 | 11 | 16 | 4 | 7 | 0.186 |
| mapa padrão (9 vértices, 11 arestas) | DFS (pilha) | 9 | 17 | 36 | 13 | 10 | 16 | 4 | 7 | 0.191 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | BFS | 7 | 59 | 171 | 86 | 29 | 86 | 6 | 42 | 0.659 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | DFS (recursiva) | 35 | 36 | 55 | 20 | 36 | 36 | 6 | 15 | 0.546 |
| mapa gerado (30 vértices, 44 arestas, seed 2042) | DFS (pilha) | 35 | 36 | 130 | 38 | 58 | 36 | 6 | 15 | 0.689 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | BFS | 8 | 181 | 556 | 339 | 38 | 218 | 8 | 86 | 2.051 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | DFS (recursiva) | 44 | 235 | 604 | 370 | 63 | 93 | 7 | 44 | 2.569 |
| mapa gerado (60 vértices, 89 arestas, seed 2042) | DFS (pilha) | 44 | 235 | 709 | 389 | 104 | 93 | 7 | 44 | 3.269 |

BFS encontra o menor número de ações porque cada ação custa 1. A DFS não tem essa garantia: a rota encontrada tende a ser mais longa, e o número de estados expandidos pode ser menor ou maior que o da BFS, conforme a ordem dos vizinhos e a posição do objetivo. Complexidade: O(|V| + |E|) no grafo de estados, cujo tamanho cresce com o número de combinações de posição, pistas e portas.

## 3. Árvore AVL — altura × número de nós

| nós | altura | log2(n) | rotações | tempo total de inserção (ms) |
|---:|---:|---:|---:|---:|
| 15 | 3 | 3.91 | 11 | 0.018 |
| 100 | 6 | 6.64 | 93 | 0.155 |
| 1000 | 9 | 9.97 | 990 | 1.876 |
| 10000 | 13 | 13.29 | 9986 | 26.619 |

Inserindo chaves em ordem crescente, uma árvore binária de busca comum degeneraria em lista (altura n − 1). A AVL mantém a altura próxima de log2(n), por isso busca e inserção custam O(log n) (aula 08).
