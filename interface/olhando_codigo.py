"""
"OLHANDO O CÓDIGO": a execução REAL de um algoritmo, linha a linha.

Como funciona
    sys.settrace pede ao próprio Python que avise antes de executar cada linha.
    O rastreador só anota as linhas do arquivo do algoritmo (por exemplo,
    algoritmos/ordenacao.py) e, a cada uma, guarda:
        - o número da linha no arquivo real;
        - o estado naquele instante (o vetor, o auxiliar B, os índices);
        - os contadores de comparações e movimentações;
        - uma explicação didática e uma técnica.
    A página do jogo só reproduz essa gravação: nenhuma linha é escrita à mão,
    então a linha acesa é sempre a que o Python executou.

    O evento 'line' acontece ANTES de a linha rodar: o passo mostra o estado
    no momento em que aquela linha vai ser executada.
"""
import inspect
import os
import sys

from algoritmos import ordenacao

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_PASSOS = 400

# Linhas de medição de tempo e de preparação: não ajudam a entender o algoritmo.
_IGNORAR = ("perf_counter", "Contador(", "tempo_ms", "_garantir_pilha", "return c")


def _rel(caminho):
    return os.path.relpath(caminho, RAIZ).replace(os.sep, "/")


def codigo_de(funcoes):
    """Linhas reais (número, texto) das funções, sem as docstrings (o pseudocódigo do slide)."""
    linhas = []
    for f in funcoes:
        fonte, inicio = inspect.getsourcelines(f)
        dentro_doc, aspas = False, 0
        for k, texto in enumerate(fonte):
            t = texto.strip()
            if t.startswith('"""') or (dentro_doc and '"""' in t):
                aspas += t.count('"""')
                dentro_doc = aspas % 2 == 1
                continue
            if dentro_doc:
                continue
            linhas.append([inicio + k, texto.rstrip("\n")])
        linhas.append([None, ""])
    return linhas


class Rastreador:
    def __init__(self, arquivo, anotar):
        self.arquivo = os.path.abspath(arquivo)
        self.anotar = anotar          # função(frame, linha, texto) -> dict do passo (ou None para pular)
        self.passos = []
        self.fonte = open(self.arquivo, encoding="utf-8").read().split("\n")

    def _trace(self, frame, evento, arg):
        if os.path.abspath(frame.f_code.co_filename) != self.arquivo:
            return None
        if evento == "line" and len(self.passos) < MAX_PASSOS:
            texto = self.fonte[frame.f_lineno - 1].strip()
            if not texto.startswith("#") and not any(x in texto for x in _IGNORAR):
                p = self.anotar(frame, frame.f_lineno, texto)
                if p is not None:
                    p["linha"] = frame.f_lineno
                    self.passos.append(p)
        return self._trace

    def rodar(self, func, *args):
        antigo = sys.gettrace()
        sys.settrace(self._trace)
        try:
            return func(*args)
        finally:
            sys.settrace(antigo)


# ============================================================ FASE 1: ordenação
def _locais(frame):
    """Variáveis da linha atual, inclusive as das funções de fora (A, B, c nas funções internas)."""
    return dict(frame.f_locals)


def gravar_ordenacao(registros, algoritmo, chave):
    """
    Roda o algoritmo de verdade sobre uma CÓPIA dos registros e devolve a gravação.
    Os registros aparecem pelo id; a chave composta decide a ordem.
    """
    A = list(registros)
    ids = {id(r): r.id_registro for r in A}
    nome = lambda r: ids.get(id(r), "—") if r is not None else None
    rotulo = lambda r: f"{r.id_registro} (zona {r.zona}, seção {r.secao}, {r.timestamp})"

    ultimo = {"comp": 0, "mov": 0, "aux": None}

    def anotar(frame, linha, texto):
        L = _locais(frame)
        c = L.get("c")
        i, j, k, p, q, r, x = (L.get(n) for n in "ijkpqrx")
        B = L.get("B")
        if c is not None:                 # funções internas que não usam 'c' não o enxergam: vale o último valor
            ultimo["comp"], ultimo["mov"] = c.comparacoes, c.movimentacoes
        if isinstance(B, list):
            ultimo["aux"] = [nome(e) for e in B]
        passo = {"vetor": [nome(e) for e in A], "aux": ultimo["aux"],
                 "comp": ultimo["comp"], "mov": ultimo["mov"],
                 "destaque": [], "faixa": None, "did": "", "tec": ""}
        ints = lambda *v: all(isinstance(t, int) for t in v)
        if ints(p, r):
            passo["faixa"] = [p, r]
        if algoritmo == "merge" and ints(k, r) and "B" in L and isinstance(L.get("B"), list) and frame.f_code.co_name == "merge":
            passo["antigos"] = list(range(k, r + 1))    # ainda guardam o valor antigo: o merge vai sobrescrevê-las
        # ---------- Bubble ----------
        if texto.startswith("for j in range(n - 1, 0, -1)"):
            passo["did"] = "Começa uma passada: o maior registro ainda fora do lugar vai 'borbulhar' até o fim da parte não ordenada."
            passo["tec"] = f"j = {j} (última posição desta passada)" if j is not None else "j vai de n−1 até 1"
        elif texto.startswith("for i in range(0, j)"):
            passo["did"] = "Anda pelos pares vizinhos, da esquerda para a direita."
            passo["tec"] = f"i = {i}, j = {j}"
        elif texto.startswith("if chave(A[i]) > chave(A[i + 1])") and ints(i):
            fora = chave(A[i]) > chave(A[i + 1])
            passo["destaque"] = [i, i + 1]
            passo["did"] = f"Compara {A[i].id_registro} com {A[i + 1].id_registro}: " + ("estão fora de ordem, vai trocar." if fora else "já estão em ordem, segue.")
            passo["tec"] = f"chave(A[{i}]) > chave(A[{i + 1}])? {'sim' if fora else 'não'}\nA[{i}] = {rotulo(A[i])}\nA[{i + 1}] = {rotulo(A[i + 1])}"
        elif texto.startswith("aux = A[i]") and ints(i):
            passo["destaque"] = [i, i + 1]
            passo["did"] = f"Guarda {A[i].id_registro} numa variável auxiliar, para não perdê-lo na troca."
            passo["tec"] = f"aux ← A[{i}]"
        elif texto.startswith("A[i] = A[i + 1]") and ints(i):
            passo["destaque"] = [i, i + 1]
            passo["did"] = f"Põe {A[i + 1].id_registro} na posição {i}."
            passo["tec"] = f"A[{i}] ← A[{i + 1}]"
        elif texto.startswith("A[i + 1] = aux") and ints(i):
            passo["destaque"] = [i, i + 1]
            passo["did"] = "Põe o registro guardado na posição seguinte: troca concluída."
            passo["tec"] = f"A[{i + 1}] ← aux (uma troca = 3 movimentações)"
        # ---------- Merge ----------
        elif texto.startswith("if p < r:") and ints(p, r):
            passo["did"] = (f"Olha o trecho das posições {p} a {r}. " + (("Tem mais de um registro: divide ao meio." if algoritmo == "merge" else "Tem mais de um registro: escolhe um pivô e separa.")
                            if p < r else "Tem no máximo um registro: já está ordenado (caso-base, a recursão para aqui)."))
            passo["tec"] = f"p = {p}, r = {r}; p < r? {'sim' if p < r else 'não — caso-base'}"
        elif texto.startswith("q = (p + r) // 2") and ints(p, r):
            passo["did"] = f"Acha o meio do trecho {p}…{r}."
            passo["tec"] = f"q = ⌊({p} + {r}) / 2⌋ = {(p + r) // 2}"
        elif texto.startswith("ordena(p, q)") and ints(p, q):
            passo["did"] = f"Chamada recursiva: ordena a metade esquerda ({p}…{q})."
            passo["tec"] = f"mergeSort(A, {p}, {q})"
        elif texto.startswith("ordena(q + 1, r)") and ints(q, r) and algoritmo == "merge":
            passo["did"] = f"Chamada recursiva: ordena a metade direita ({q + 1}…{r})."
            passo["tec"] = f"mergeSort(A, {q + 1}, {r})"
        elif texto.startswith("merge(p, q, r)") and ints(p, q, r):
            passo["did"] = f"As duas metades já estão em ordem: agora intercala {p}…{q} com {q + 1}…{r}."
            passo["tec"] = f"merge(A, {p}, {q}, {r})"
        elif texto.startswith("B[i] = A[i]") and ints(i):
            passo["destaque"] = [i]
            passo["did"] = f"Copia {A[i].id_registro} para o vetor auxiliar B."
            passo["tec"] = f"B[{i}] ← A[{i}]"
        elif texto.startswith("B[q + 1 + r - j] = A[j]") and ints(q, r, j):
            passo["destaque"] = [j]
            passo["did"] = f"Copia {A[j].id_registro} para B, com a metade direita de trás para a frente (assim não precisa de sentinela)."
            passo["tec"] = f"B[{q + 1 + r - j}] ← A[{j}]"
        elif texto.startswith("if chave(B[i]) <= chave(B[j])") and ints(i, j, k):
            menor = chave(B[i]) <= chave(B[j])
            passo["destaque"] = [k]
            passo["did"] = f"Compara {B[i].id_registro} (esquerda) com {B[j].id_registro} (direita): o menor vai para a posição {k}" + (" — empate ou esquerda menor: vem da esquerda." if menor else " — vem da direita.")
            passo["tec"] = f"chave(B[{i}]) <= chave(B[{j}])? {'sim' if menor else 'não'}"
            passo["auxDestaque"] = [i, j]
        elif texto.startswith("A[k] = B[i]") and ints(k, i):
            passo["destaque"] = [k]; passo["auxDestaque"] = [i]
            passo["did"] = f"{B[i].id_registro} entra na posição {k}."
            passo["tec"] = f"A[{k}] ← B[{i}]"
        elif texto.startswith("A[k] = B[j]") and ints(k, j):
            passo["destaque"] = [k]; passo["auxDestaque"] = [j]
            passo["did"] = f"{B[j].id_registro} entra na posição {k}."
            passo["tec"] = f"A[{k}] ← B[{j}]"
        # ---------- Quick ----------
        elif texto.startswith("q = _particiona(") and ints(p, r):
            passo["destaque"] = [r]
            passo["did"] = f"Particiona o trecho {p}…{r} usando o último registro, {A[r].id_registro}, como pivô."
            passo["tec"] = f"q ← particiona(A, {p}, {r})"
        elif texto.startswith("ordena(p, q - 1)") and ints(p, q):
            passo["destaque"] = [q]
            passo["did"] = f"O pivô já está no lugar certo (posição {q}). Ordena o lado dos menores ({p}…{q - 1})."
            passo["tec"] = f"quickSort(A, {p}, {q - 1})"
        elif texto.startswith("ordena(q + 1, r)") and ints(q, r):
            passo["did"] = f"Ordena o lado dos maiores ({q + 1}…{r})."
            passo["tec"] = f"quickSort(A, {q + 1}, {r})"
        elif texto.startswith("x = chave(A[r])") and ints(r):
            passo["destaque"] = [r]
            passo["did"] = f"O pivô é {A[r].id_registro}, o último do trecho."
            passo["tec"] = f"x ← chave(A[{r}])"
        elif texto.startswith("if chave(A[j]) <= x") and ints(j, r):
            menor = chave(A[j]) <= chave(A[r])
            passo["destaque"] = [j, r]
            passo["did"] = f"{A[j].id_registro} vem antes do pivô {A[r].id_registro}? " + ("Sim: vai para o lado dos menores." if menor else "Não: fica no lado dos maiores.")
            passo["tec"] = f"chave(A[{j}]) <= x? {'sim' if menor else 'não'}; i = {i}"
        elif texto.startswith("A[i], A[j] = A[j], A[i]") and ints(i, j):
            passo["destaque"] = [i, j]
            passo["did"] = f"Troca {A[i].id_registro} e {A[j].id_registro}: o menor passa para o lado esquerdo."
            passo["tec"] = f"troca A[{i}] e A[{j}]"
        elif texto.startswith("A[i + 1], A[r] = A[r], A[i + 1]") and ints(i, r):
            passo["destaque"] = [i + 1, r]
            passo["did"] = f"Põe o pivô {A[r].id_registro} na posição {i + 1}: à esquerda só menores, à direita só maiores."
            passo["tec"] = f"troca A[{i + 1}] e A[{r}]"
        elif texto.startswith("return i + 1") and ints(i):
            passo["destaque"] = [i + 1]
            passo["did"] = f"O pivô ficou na posição {i + 1}, que já é a definitiva."
            passo["tec"] = f"retorna q = {i + 1}"
        else:
            return None                                   # linhas de contagem e de controle: não viram passo
        return passo

    funcoes = {"bubble": [ordenacao.bubble_sort], "merge": [ordenacao.merge_sort],
               "quick": [ordenacao.quick_sort, ordenacao._particiona]}[algoritmo]
    tr = Rastreador(ordenacao.__file__, anotar)
    c = tr.rodar(ordenacao.ordenar, A, algoritmo, chave)
    tr.passos.append({"linha": None, "vetor": [nome(e) for e in A], "aux": None, "comp": c.comparacoes,
                      "mov": c.movimentacoes, "destaque": [], "faixa": None, "fim": True,
                      "did": f"Pronto: {len(A)} registros em ordem, com {c.comparacoes} comparações e {c.movimentacoes} movimentações.",
                      "tec": f"{c.algoritmo}: {c.comparacoes} comparações, {c.movimentacoes} movimentações."})
    return {"arquivo": _rel(ordenacao.__file__), "codigo": codigo_de(funcoes), "passos": tr.passos,
            "registros": {r.id_registro: [r.zona, r.secao, r.timestamp] for r in registros}}


def dados_motor_fase1(registros, chave, n=8):
    """A gravação dos três algoritmos sobre os primeiros n registros do lote embaralhado."""
    amostra = list(registros)[:n]
    return {"n": n, "total": len(registros),
            "algoritmos": {alg: gravar_ordenacao(amostra, alg, chave) for alg in ("bubble", "merge", "quick")}}
