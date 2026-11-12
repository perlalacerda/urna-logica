"""
Algoritmos de ordenação — Bubble, Merge e Quick Sort.   [Aulas 02 e 04]

Todos ordenam o vetor A "no lugar" (in-place) em ordem CRESCENTE e
devolvem um Contador com as métricas pedidas no EP (seção 15.1).

Como ordenar registros por mais de um campo?
    Cada algoritmo recebe uma função 'chave' que transforma o elemento num
    valor comparável. Para a Fase 1 a chave é uma TUPLA:
        chave(r) = (r.zona, r.secao, r.timestamp, r.id_registro)
    Python compara tuplas campo a campo, como no dicionário: só olha o 2º
    campo quando o 1º empata, e assim por diante (ordem lexicográfica).
    Isso é a "chave composta" pedida no enigma 5.3.

O que contamos:
    comparacoes   = quantas vezes comparamos duas chaves (A[i] > A[i+1], etc.)
    movimentacoes = quantas vezes um elemento é escrito numa posição
                    (do vetor A, do auxiliar B ou da variável aux).
                    Uma troca com aux conta 3; uma cópia conta 1.

Complexidade (aulas 03 e 04):
                  melhor        médio         pior        estável?
    Bubble        Θ(n²)         Θ(n²)         Θ(n²)       sim
    Merge         Θ(n log n)    Θ(n log n)    Θ(n log n)  não, nesta versão*
    Quick         Θ(n log n)    Θ(n log n)    Θ(n²)       não
    (*) o merge da aula copia a metade direita invertida para B; isso
        dispensa sentinela, mas pode trocar a ordem de chaves iguais.
"""

import sys
import time


def _identidade(x):
    return x


class Contador:
    def __init__(self, algoritmo):
        self.algoritmo = algoritmo
        self.comparacoes = 0
        self.movimentacoes = 0
        self.tempo_ms = 0.0

    def __repr__(self):
        return (f"{self.algoritmo}: {self.comparacoes} comparações, "
                f"{self.movimentacoes} movimentações, {self.tempo_ms:.3f} ms")


# ==================================================================== BUBBLE
def bubble_sort(A, chave=_identidade):
    """
    bubbleSort (A[0..n-1], n)                          [Aula 02, slide 10]
    1. para (j = n-1; j >= 1; j--) faça
    2.     para (i = 0; i <= j-1; i++) faça
    3.         se (A[i] > A[i+1]) então
    4.             aux <- A[i]
    5.             A[i] <- A[i+1]
    6.             A[i+1] <- aux

    Ideia: a cada passada j, o maior elemento ainda fora do lugar
    "borbulha" até a posição j. Depois da passada j, A[j..n-1] está pronto.
    Comparações: (n-1) + (n-2) + ... + 1 = n(n-1)/2 = Θ(n²), sempre.
    """
    c = Contador("Bubble Sort")
    inicio = time.perf_counter()
    n = len(A)
    for j in range(n - 1, 0, -1):                  # 1: j = n-1 ... 1
        for i in range(0, j):                      # 2: i = 0 ... j-1
            c.comparacoes += 1
            if chave(A[i]) > chave(A[i + 1]):      # 3
                aux = A[i]                         # 4
                A[i] = A[i + 1]                    # 5
                A[i + 1] = aux                     # 6
                c.movimentacoes += 3
    c.tempo_ms = (time.perf_counter() - inicio) * 1000
    return c


def bubble_sort_recursivo(A, chave=_identidade):
    """
    bubbleSort (A[0..n-1], n)  — versão recursiva      [Aula 02, slide 15]
    1. se (n = 1) então retorna        // caso-base: A[0] está ordenado
    3. para (i = 0; i <= n-2; i++) faça
    4.     se (A[i] > A[i+1]) então troca A[i] e A[i+1]
    8. bubbleSort (A[0..n-2], n-1)     // chamada recursiva com problema menor
    """
    c = Contador("Bubble Sort (recursivo)")
    inicio = time.perf_counter()

    def bubble(n):
        if n <= 1:                                 # 1-2: caso-base (n=0 também)
            return
        for i in range(0, n - 1):                  # 3
            c.comparacoes += 1
            if chave(A[i]) > chave(A[i + 1]):      # 4
                A[i], A[i + 1] = A[i + 1], A[i]
                c.movimentacoes += 3
        bubble(n - 1)                              # 8

    _garantir_pilha_de_recursao(len(A))
    bubble(len(A))
    c.tempo_ms = (time.perf_counter() - inicio) * 1000
    return c


# ==================================================================== MERGE
def merge_sort(A, chave=_identidade):
    """
    mergeSort (A[p..r], p, r)                          [Aula 02, slide 20]
    1. se (p < r) então
    2.     q <- piso((p+r)/2)
    3.     mergeSort (A[p..q], p, q)
    4.     mergeSort (A[q+1..r], q+1, r)
    5.     merge (A[p..r], p, q, r)

    Divisão e conquista: divide ao meio, ordena cada metade, intercala.
    Recorrência: T(n) = 2T(n/2) + Θ(n)  =>  T(n) = Θ(n log n)   [Aula 04]
    """
    c = Contador("Merge Sort")
    inicio = time.perf_counter()
    B = [None] * len(A)                            # vetor auxiliar B[p..r]

    def merge(p, q, r):
        """
        merge (A[p..r], p, q, r)                       [Aula 02, slide 21]
        1. para (i = p; i <= q; i++) faça  B[i] <- A[i]
        3. para (j = q+1; j <= r; j++) faça  B[q+1+r-j] <- A[j]   // invertida
        5. i <- p
        6. j <- r
        7. para (k = p; k <= r; k++) faça
        8.     se (B[i] <= B[j]) então A[k] <- B[i]; i <- i+1
        11.    senão A[k] <- B[j]; j <- j-1
        """
        for i in range(p, q + 1):                  # 1-2
            B[i] = A[i]
            c.movimentacoes += 1
        for j in range(q + 1, r + 1):              # 3-4
            B[q + 1 + r - j] = A[j]
            c.movimentacoes += 1
        i, j = p, r                                # 5-6
        for k in range(p, r + 1):                  # 7
            c.comparacoes += 1
            if chave(B[i]) <= chave(B[j]):         # 8
                A[k] = B[i]                        # 9
                i += 1                             # 10
            else:                                  # 11
                A[k] = B[j]                        # 12
                j -= 1                             # 13
            c.movimentacoes += 1

    def ordena(p, r):
        if p < r:                                  # 1 (caso-base: p >= r, 0 ou 1 elemento)
            q = (p + r) // 2                       # 2
            ordena(p, q)                           # 3
            ordena(q + 1, r)                       # 4
            merge(p, q, r)                         # 5

    ordena(0, len(A) - 1)
    c.tempo_ms = (time.perf_counter() - inicio) * 1000
    return c


# ==================================================================== QUICK
def quick_sort(A, chave=_identidade):
    """
    quickSort (A[p..r], p, r)                          [Aula 04, slide 31]
    1. se (p < r) então
    2.     q <- particiona(A[p..r], p, r)
    3.     quickSort (A[p..q-1], p, q-1)     <-- ver observação
    4.     quickSort (A[q+1..r], q+1, r)

    Observação: o slide escreve 'quickSort(A[p..q], p, q)'. Com este
    particiona (pivô no fim), o pivô já está na posição final q; se ele for
    o maior valor, q = r e 'quickSort(p, q)' repetiria a mesma chamada para
    sempre. Por isso usamos p..q-1, como no livro de Cormen.
    (Ver quick_sort_versao_do_slide e o teste que demonstra o problema.)

    Pior caso (vetor já ordenado ou invertido): T(n) = T(n-1) + Θ(n) = Θ(n²)
    Melhor caso / caso médio: Θ(n log n)                         [Aula 04]
    """
    c = Contador("Quick Sort")
    inicio = time.perf_counter()

    def ordena(p, r):
        if p < r:                                  # 1 (caso-base: p >= r)
            q = _particiona(A, p, r, chave, c)     # 2
            ordena(p, q - 1)                       # 3
            ordena(q + 1, r)                       # 4

    _garantir_pilha_de_recursao(len(A))
    ordena(0, len(A) - 1)
    c.tempo_ms = (time.perf_counter() - inicio) * 1000
    return c


def _particiona(A, p, r, chave, c):
    """
    particiona (A[p..r], p, r)                         [Aula 04, slide 32]
    1. x <- A[r]                // pivô = último elemento
    2. i <- p-1
    3. para (j = p; j <= r-1; j++) faça
    4.     se (A[j] <= x) então
    5.         i <- i+1
    6.         troca A[i] e A[j]
    7. troca A[i+1] e A[r]
    8. retorne i+1
    Ao final: A[p..q-1] <= pivô < A[q+1..r], e o pivô está em q.   Θ(n)
    """
    x = chave(A[r])                                # 1
    i = p - 1                                      # 2
    for j in range(p, r):                          # 3: j = p ... r-1
        c.comparacoes += 1
        if chave(A[j]) <= x:                       # 4
            i += 1                                 # 5
            A[i], A[j] = A[j], A[i]                # 6
            c.movimentacoes += 3
    A[i + 1], A[r] = A[r], A[i + 1]                # 7
    c.movimentacoes += 3
    return i + 1                                   # 8


def quick_sort_versao_do_slide(A, chave=_identidade):
    """
    Versão LITERAL do slide 31 (recursão em p..q). Existe apenas para o teste
    que demonstra o laço infinito; NÃO é usada pelo jogo.
    Em Python, o laço infinito aparece como RecursionError.
    """
    c = Contador("Quick Sort (slide literal)")

    def ordena(p, r):
        if p < r:
            q = _particiona(A, p, r, chave, c)
            ordena(p, q)
            ordena(q + 1, r)

    ordena(0, len(A) - 1)
    return c


# ==================================================================== apoio
ALGORITMOS = {
    "bubble": bubble_sort,
    "merge": merge_sort,
    "quick": quick_sort,
}


def ordenar(A, algoritmo, chave=_identidade):
    """Ponto único usado pelo jogo: ordenar(A, 'merge', chave)."""
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}. Use: {', '.join(ALGORITMOS)}")
    return ALGORITMOS[algoritmo](A, chave)


def primeiro_fora_de_ordem(A, chave=_identidade):
    """
    Devolve o primeiro índice i tal que A[i] > A[i+1] (ordem violada),
    ou -1 se o vetor está em ordem crescente. Usado no feedback da Fase 1.
    """
    for i in range(len(A) - 1):
        if chave(A[i]) > chave(A[i + 1]):
            return i
    return -1


def _garantir_pilha_de_recursao(n):
    """
    Bubble recursivo e Quick Sort no pior caso empilham ~n chamadas.
    O Python limita a profundidade de recursão (padrão: 1000); aumentamos o
    limite quando o vetor é grande. Limitação registrada no relatório.
    """
    necessario = n + 200
    if sys.getrecursionlimit() < necessario:
        sys.setrecursionlimit(necessario)
