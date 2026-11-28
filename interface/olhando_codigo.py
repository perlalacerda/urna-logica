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


# ============================================================ FASE 3: busca no mapa
def _rotulo_estado(e):
    pos, pistas, portas, energia = e
    return f"{pos} {{{','.join(pistas)}}} ⚡{energia}"


def gravar_bfs_aula():
    """BFS da aula 09 no grafo do mapa (sem pistas nem portas): cores, distâncias e a fila Q."""
    from algoritmos import busca_grafo
    from jogo.fase3 import construir_mapa
    G = construir_mapa()
    NOMES = {busca_grafo.BRANCO: "branco", busca_grafo.CINZA: "cinza", busca_grafo.PRETO: "preto"}

    def anotar(frame, linha, texto):
        if frame.f_code.co_name != "bfs":
            return None
        L = _locais(frame)
        cor, d, Q, u, v = L.get("cor") or {}, L.get("d") or {}, L.get("Q"), L.get("u"), L.get("v")
        fila = Q.para_lista() if Q is not None and hasattr(Q, "para_lista") else []
        dist = {k: (None if x == busca_grafo.INFINITO else x) for k, x in d.items()}
        passo = {"mapa": {"u": u, "v": v, "cores": {k: NOMES.get(x, "branco") for k, x in cor.items()}, "d": dist},
                 "estrutura": {"nome": "Fila Q (o primeiro a entrar é o primeiro a sair)", "itens": list(fila)},
                 "cont": [sum(1 for x in cor.values() if x == busca_grafo.PRETO), len(fila)], "did": "", "tec": ""}
        if texto.startswith("for u in G.vertices()"):
            passo["did"] = "Prepara todos os locais: brancos (ainda não descobertos), com distância infinita."
            passo["tec"] = "cor[u] ← BRANCO; d[u] ← ∞; π[u] ← NULL"
        elif texto.startswith("cor[u], d[u], pi[u]"):
            return None
        elif texto.startswith("cor[s], d[s], pi[s]"):
            passo["did"] = "A Central de Auditoria (A) é o ponto de partida: fica cinza (descoberta) e com distância 0."
            passo["tec"] = "cor[s] ← CINZA; d[s] ← 0; π[s] ← NULL"
        elif texto.startswith("Q = Fila()"):
            passo["did"] = "Cria a fila vazia."
            passo["tec"] = "Q ← ∅"
        elif texto.startswith("Q.enqueue(s)"):
            passo["did"] = "Põe A na fila."
            passo["tec"] = "enqueue(Q, s)"
        elif texto.startswith("while not Q.esta_vazia()"):
            passo["did"] = "Enquanto houver alguém na fila, a busca continua." if fila else "A fila esvaziou: todos os locais alcançáveis foram visitados."
            passo["tec"] = f"Q ≠ ∅? {'sim' if fila else 'não — fim'}"
        elif texto.startswith("_, u = Q.dequeue()"):
            passo["did"] = f"Tira da frente da fila o próximo local: {fila[0] if fila else '—'}."
            passo["tec"] = f"u ← dequeue(Q) = {fila[0] if fila else '—'}"
        elif texto.startswith("ordem.append(u)"):
            return None
        elif texto.startswith("for v in G.vizinhos(u)"):
            passo["did"] = f"Olha os vizinhos de {u}: {', '.join(G.vizinhos(u))}." if u else ""
            passo["tec"] = f"para cada v em Adj[{u}]"
        elif texto.startswith("if cor[v] == BRANCO") and v:
            branco = cor.get(v) == busca_grafo.BRANCO
            passo["did"] = f"{v} ainda não foi descoberto? " + ("Sim: vai entrar na fila." if branco else "Não: já foi descoberto, segue.")
            passo["tec"] = f"cor[{v}] = {NOMES.get(cor.get(v))}"
        elif texto.startswith("cor[v] = CINZA") and v:
            passo["did"] = f"{v} acaba de ser descoberto: fica cinza."
            passo["tec"] = f"cor[{v}] ← CINZA"
        elif texto.startswith("d[v] = d[u] + 1") and v:
            passo["did"] = f"{v} está a um corredor a mais que {u}: distância {dist.get(u, 0) + 1}."
            passo["tec"] = f"d[{v}] ← d[{u}] + 1 = {dist.get(u, 0) + 1}"
        elif texto.startswith("pi[v] = u") and v:
            passo["did"] = f"Anota que chegou a {v} vindo de {u} (é assim que o caminho é refeito depois)."
            passo["tec"] = f"π[{v}] ← {u}"
        elif texto.startswith("Q.enqueue(v)") and v:
            passo["did"] = f"{v} entra no fim da fila."
            passo["tec"] = f"enqueue(Q, {v})"
        elif texto.startswith("cor[u] = PRETO") and u:
            passo["did"] = f"Todos os vizinhos de {u} foram vistos: {u} fica preto (terminado)."
            passo["tec"] = f"cor[{u}] ← PRETO"
        elif texto.startswith("return d, pi"):
            passo["did"] = "Fim: cada local tem sua distância em corredores a partir de A."
            passo["tec"] = "d = " + ", ".join(f"{k}:{x}" for k, x in sorted(dist.items()))
        else:
            return None
        return passo

    tr = Rastreador(busca_grafo.__file__, anotar)
    tr.rodar(busca_grafo.bfs, G, "A")
    return {"arquivo": _rel(busca_grafo.__file__), "codigo": codigo_de([busca_grafo.bfs]), "passos": tr.passos,
            "rotulos": ["Locais terminados (pretos)", "Tamanho da fila"],
            "nota": "BFS da aula no grafo do mapa: só os corredores, sem pistas nem portas. Mostra as distâncias em corredores a partir de A."}


def gravar_busca_solver(qual):
    """BFS ou DFS recursiva do solver no espaço de estados da Fase 3 (com pistas, portas e energia)."""
    from algoritmos import solver
    from jogo.fase3 import ProblemaMapa
    func, nomes = {"bfs": (solver.bfs, ("bfs",)), "dfs": (solver.dfs_recursiva, ("dfs_recursiva", "visita"))}[qual]

    def anotar(frame, linha, texto):
        if frame.f_code.co_name not in nomes or texto.startswith("r.") or texto.startswith("r, inicio"):
            return None
        L = _locais(frame)
        u, v = L.get("u"), L.get("v")
        if qual == "bfs":
            Q = L.get("Q")
            itens = [_rotulo_estado(e) for e in Q.para_lista()] if Q is not None else []
            nome = "Fila Q de situações"
        else:
            itens = [_rotulo_estado(e) for e in reversed(L.get("chamadas") or [])]
            nome = "Pilha de chamadas (o topo é o primeiro)"
        passo = {"mapa": {"u": u[0] if u else None, "v": v[0] if v else None},
                 "estrutura": {"nome": nome, "itens": itens},
                 "cont": [len(itens), None], "did": "", "tec": ""}
        U, V = (_rotulo_estado(u) if u else "—"), (_rotulo_estado(v) if v else "—")
        if texto.startswith("s = problema.estado_inicial()"):
            passo["did"] = "A situação inicial: na Central de Auditoria (A), sem pistas, com 10 de energia."
            passo["tec"] = "s ← (A, {}, {}, 10)"
        elif texto.startswith("visitados.marcar(s)"):
            passo["did"] = "Guarda a situação inicial na memória (a AVL de visitados)."
            passo["tec"] = "marca s na AVL"
        elif texto.startswith("Q = Fila()") or texto.startswith("Q.enqueue(s)"):
            passo["did"] = "Cria a fila e põe nela a situação inicial." if texto.startswith("Q.enqueue") else "Cria a fila vazia."
            passo["tec"] = texto
        elif texto.startswith("while not Q.esta_vazia()"):
            passo["did"] = "Enquanto houver situações na fila, a busca continua."
            passo["tec"] = f"Q ≠ ∅? {'sim' if itens else 'não'}"
        elif texto.startswith("_, u = Q.dequeue()"):
            passo["did"] = f"Tira da frente da fila a próxima situação: {itens[0] if itens else '—'}."
            passo["tec"] = "u ← dequeue(Q)"
        elif texto.startswith("chamadas.append(u)"):
            passo["did"] = f"Entra na situação {U}: ela vai para o topo da pilha de chamadas."
            passo["tec"] = f"visita({U})"
        elif texto.startswith("if problema.eh_objetivo(u)"):
            achou = u is not None and u[0] == "F"
            passo["did"] = f"Chegou ao Centro de Validação (F)? " + ("Sim! Achou o caminho." if achou else "Ainda não.")
            passo["tec"] = f"u = {U}; objetivo? {'sim' if achou else 'não'}"
        elif texto.startswith("for acao, v, _ in problema.sucessores(u)"):
            passo["did"] = f"Gera as próximas situações a partir de {U}, pelas regras do jogo (corredor, porta, energia)."
            passo["tec"] = "para cada sucessor v de u"
        elif texto.startswith("if visitados.eh_repetido(v)"):
            passo["did"] = f"A situação {V} já está na memória? A AVL responde."
            passo["tec"] = f"chave = ({', '.join(map(str, v))})" if v else ""
        elif texto.startswith("continue"):
            passo["did"] = f"{V} é repetida: não explora de novo."
            passo["tec"] = "repetido → continue"
        elif texto.startswith("visitados.marcar(v)"):
            passo["did"] = f"{V} é nova: guarda na memória."
            passo["tec"] = "marca v na AVL"
        elif texto.startswith("pais[v] = (u, acao)"):
            passo["did"] = f"Anota que {V} veio de {U}, para refazer o caminho no fim."
            passo["tec"] = "π[v] ← u"
        elif texto.startswith("Q.enqueue(v)"):
            passo["did"] = f"{V} entra no fim da fila."
            passo["tec"] = "enqueue(Q, v)"
        elif texto.startswith("achado = visita(v, profundidade + 1)"):
            passo["did"] = f"Mergulha em {V}: chamada recursiva (a pilha cresce)."
            passo["tec"] = "visita(v)  ← chamada recursiva"
        elif texto.startswith("if achado is not None"):
            passo["did"] = "A chamada de baixo achou o objetivo? Se sim, devolve a resposta para cima."
            passo["tec"] = "condição de retorno"
        elif texto.startswith("return u"):
            passo["did"] = "Achou o Centro de Validação: devolve a situação final."
            passo["tec"] = "caso-base 1: objetivo"
        elif texto.startswith("chamadas.pop()"):
            passo["did"] = f"Nenhum caminho saindo de {U} chega a F: beco sem saída, volta atrás."
            passo["tec"] = "caso-base 2: desempilha"
        elif texto.startswith("return achado"):
            passo["did"] = "Repassa a resposta para a chamada de cima."
            passo["tec"] = "return achado"
        else:
            return None
        return passo

    tr = Rastreador(solver.__file__, anotar)
    res = tr.rodar(func, ProblemaMapa())
    cortado = len(tr.passos) >= MAX_PASSOS
    caminho = " → ".join(e[0] for _, e in res.caminho)
    tr.passos.append({"linha": None, "fim": True, "mapa": {"u": "F", "v": None}, "estrutura": {"nome": "", "itens": []},
                      "cont": [res.expandidos, res.repetidos],
                      "did": (f"(A gravação mostra as primeiras {MAX_PASSOS} linhas.) " if cortado else "") +
                             f"Resultado: {res.numero_acoes()} passos, {caminho}. Explorou {res.expandidos} situações e barrou {res.repetidos} repetidas.",
                      "tec": f"{res.algoritmo}: expandidos={res.expandidos}, repetidos={res.repetidos}, fronteira máxima={res.maior_fronteira}"})
    funcs = [solver.bfs] if qual == "bfs" else [solver.dfs_recursiva]
    return {"arquivo": _rel(solver.__file__), "codigo": codigo_de(funcs), "passos": tr.passos,
            "rotulos": ["Na fila" if qual == "bfs" else "Na pilha", "Repetidos (no fim)"],
            "nota": ("BFS do solver, a que o jogo usa: cada situação é (local, pistas, portas, energia)."
                     if qual == "bfs" else "DFS recursiva do solver: mergulha fundo e volta atrás nos becos sem saída.")}


def dados_motor_fase3():
    return {"algoritmos": {"bfs_aula": gravar_bfs_aula(), "bfs": gravar_busca_solver("bfs"), "dfs": gravar_busca_solver("dfs")}}


# ============================================================ FASE 4: AVL
def gravar_avl(sequencia):
    """Inserção real dos códigos na AVL (estruturas/avl.py), com a árvore desenhada a cada passo."""
    from estruturas import avl as mod
    from interface.visualizacao import arvore_para_dict
    T = mod.ArvoreAVL()
    estado = {"antes": None}

    def contem(n, alvo):
        return n is not None and (n is alvo or contem(n.esq, alvo) or contem(n.dir, alvo))

    NOMES = {"RD": "rotação à direita (RD)", "RE": "rotação à esquerda (RE)",
             "RED": "rotação dupla esquerda-direita (RED)", "RDE": "rotação dupla direita-esquerda (RDE)"}

    def anotar(frame, linha, texto):
        fn = frame.f_code.co_name
        if fn not in ("inserir", "_insere", "_rotacao_direita", "_rotacao_esquerda",
                      "_rotacao_esquerda_direita", "_rotacao_direita_esquerda"):
            return None
        L = _locais(frame)
        x, r, p = L.get("chave"), L.get("r"), L.get("p")
        no = r if isinstance(r, mod.NoAVL) else p if isinstance(p, mod.NoAVL) else None
        if fn == "inserir" and texto.startswith("self.raiz = self._insere"):
            estado["antes"] = arvore_para_dict(T.raiz)          # o cofre completo, antes desta inserção
        # a parte em trabalho: no meio de um giro os ponteiros ficam soltos, então mostramos as peças
        pecas = []
        if fn.startswith("_rotacao_") and isinstance(p, mod.NoAVL):
            topo = L.get("u") or L.get("y")
            if isinstance(topo, mod.NoAVL):
                pecas.append([f"subárvore de {topo.chave}", arvore_para_dict(topo)])
            if not (isinstance(topo, mod.NoAVL) and contem(topo, p)):
                pecas.append([f"subárvore de {p.chave}", arvore_para_dict(p)])
        elif fn == "_insere" and isinstance(r, mod.NoAVL):
            pecas.append([f"subárvore de {r.chave}", arvore_para_dict(r)])
        passo = {"arvore": estado["antes"], "pecas": pecas, "foco": no.chave if no else None,
                 "cont": [T.quantidade, sum(T.rotacoes.values())], "did": "", "tec": ""}
        fb = (mod.altura(no.esq) - mod.altura(no.dir)) if no else None
        if fn == "inserir":
            if not texto.startswith("self.raiz = self._insere"):
                return None
            passo["did"] = f"Vai guardar o código {x} no cofre. Começa pela raiz e desce."
            passo["tec"] = f"raiz ← insere(raiz, {x})"
        elif texto.startswith("if r is None"):
            vazio = r is None
            passo["did"] = "Chegou a um lugar vazio da árvore? " + ("Sim: o código fica aqui." if vazio else f"Não: está no nó {r.chave}.")
            passo["tec"] = f"r = {'NULL' if vazio else r.chave}"
        elif texto.startswith("return NoAVL("):
            passo["did"] = f"Cria o nó {x} como folha (altura 0)."
            passo["tec"] = "caso-base: novo nó"
        elif texto.startswith("if chave == r.chave") and r:
            passo["did"] = f"{x} já está no cofre? " + ("Sim: nada muda." if x == r.chave else "Não.")
            passo["tec"] = f"{x} == {r.chave}? {'sim' if x == r.chave else 'não'}"
        elif texto.startswith("if chave < r.chave") and r:
            esq = x < r.chave
            passo["did"] = f"{x} é menor que {r.chave}? " + ("Sim: desce para a esquerda." if esq else "Não: desce para a direita.")
            passo["tec"] = f"{x} < {r.chave}? {'sim' if esq else 'não'}"
        elif texto.startswith("r.esq = self._insere") and r:
            passo["did"] = f"Chamada recursiva: insere {x} na subárvore esquerda de {r.chave}."
            passo["tec"] = f"r.esq ← insere(r.esq, {x})"
        elif texto.startswith("r.dir = self._insere") and r:
            passo["did"] = f"Chamada recursiva: insere {x} na subárvore direita de {r.chave}."
            passo["tec"] = f"r.dir ← insere(r.dir, {x})"
        elif texto.startswith("if altura(r.esq) - altura(r.dir) ==") and r:
            alvo = 2 if "== 2" in texto else -2
            passo["did"] = f"Voltando da recursão, confere o equilíbrio de {r.chave}: fator de balanceamento = {fb}. " + ("Desequilibrou: precisa girar." if fb == alvo else "Está equilibrado.")
            passo["tec"] = f"FB({r.chave}) = hE − hD = {fb}"
        elif texto.startswith("if chave < r.esq.chave") and r:
            reta = x < r.esq.chave
            passo["did"] = f"O código {x} entrou " + ("à esquerda do filho esquerdo: formato de reta → rotação simples." if reta else "à direita do filho esquerdo: formato de curva → rotação dupla.")
            passo["tec"] = f"{x} < {r.esq.chave}? {'sim (RD)' if reta else 'não (RED)'}"
        elif texto.startswith("if chave > r.dir.chave") and r:
            reta = x > r.dir.chave
            passo["did"] = f"O código {x} entrou " + ("à direita do filho direito: formato de reta → rotação simples." if reta else "à esquerda do filho direito: formato de curva → rotação dupla.")
            passo["tec"] = f"{x} > {r.dir.chave}? {'sim (RE)' if reta else 'não (RDE)'}"
        elif texto.startswith("r = self._rotacao_") and r:
            tipo = {"direita(r)": "RD", "esquerda(r)": "RE", "esquerda_direita(r)": "RED", "direita_esquerda(r)": "RDE"}[texto.split("#")[0].strip().split("_rotacao_")[1]]
            passo["did"] = f"Aplica a {NOMES[tipo]} no nó {r.chave}."
            passo["tec"] = f"r ← {tipo}({r.chave})"
        elif texto.startswith("r.h = max(") and r:
            passo["did"] = f"Atualiza a altura de {r.chave}."
            passo["tec"] = f"h({r.chave}) ← max(hE, hD) + 1 = {max(mod.altura(r.esq), mod.altura(r.dir)) + 1}"
        elif fn.startswith("_rotacao_") and p is not None:
            u, y = L.get("u"), L.get("y")
            passo["did"] = {"u = p.esq": f"Pega o filho esquerdo de {p.chave}.", "y = p.dir": f"Pega o filho direito de {p.chave}.",
                            "p.esq = u.dir": "O que estava à direita do filho passa a ser o filho esquerdo de " + str(p.chave) + ".",
                            "u.dir = p": f"{p.chave} desce e vira o filho direito de {u.chave if u else '—'}.",
                            "p.dir = y.esq": "O que estava à esquerda do filho passa a ser o filho direito de " + str(p.chave) + ".",
                            "y.esq = p": f"{p.chave} desce e vira o filho esquerdo de {y.chave if y else '—'}.",
                            "return u": f"{u.chave if u else '—'} sobe e vira a nova raiz desta parte.",
                            "return y": f"{y.chave if y else '—'} sobe e vira a nova raiz desta parte."}.get(
                texto.split("#")[0].strip(), "Recalcula as alturas depois do giro." if ".h = max(" in texto else
                "Rotação dupla: primeiro gira o filho, depois o próprio nó." if "self._rotacao_" in texto else "")
            if not passo["did"]:
                return None
            passo["tec"] = texto.split("#")[0].strip()
            passo["foco"] = p.chave
        else:
            return None
        return passo

    def inserir_todos():
        for k in sequencia:
            T.inserir(k)

    tr = Rastreador(mod.__file__, anotar)
    tr.rodar(inserir_todos)
    tr.passos.append({"linha": None, "fim": True, "arvore": arvore_para_dict(T.raiz), "foco": None,
                      "cont": [T.quantidade, sum(T.rotacoes.values())],
                      "did": f"Os {len(sequencia)} códigos estão no cofre. A árvore tem altura {T.altura()} e precisou de {sum(T.rotacoes.values())} rotações.",
                      "tec": "rotações: " + ", ".join(f"{t} em {c}" for t, c in T.historico_rotacoes)})
    A = mod.ArvoreAVL
    return {"arquivo": _rel(mod.__file__), "passos": tr.passos, "rotulos": ["Códigos já guardados", "Rotações feitas"],
            "codigo": codigo_de([A.inserir, A._insere, A._rotacao_direita, A._rotacao_esquerda,
                                 A._rotacao_esquerda_direita, A._rotacao_direita_esquerda]),
            "nota": f"Inserção dos códigos {', '.join(map(str, sequencia))} no Cofre dos Estados (árvore AVL), como na Sala 1."}


def dados_motor_fase4():
    from jogo.fase4 import SEQUENCIA_LACRES
    return {"algoritmos": {"avl": gravar_avl(SEQUENCIA_LACRES)}}


# ============================================================ FASE 2: fila, pilha e lista ligada
class RastreadorVarios(Rastreador):
    """Como o Rastreador, mas acompanha vários arquivos; cada passo diz de qual arquivo é a linha."""

    def __init__(self, arquivos, anotar, max_passos=MAX_PASSOS):
        self.arquivos = {os.path.abspath(a): open(a, encoding="utf-8").read().split("\n") for a in arquivos}
        self.anotar, self.passos, self.max_passos = anotar, [], max_passos

    def _trace(self, frame, evento, arg):
        arq = os.path.abspath(frame.f_code.co_filename)
        if arq not in self.arquivos:
            return None
        if evento == "line" and len(self.passos) < self.max_passos:
            texto = self.arquivos[arq][frame.f_lineno - 1].strip()
            if texto and not texto.startswith("#"):
                p = self.anotar(frame, frame.f_lineno, texto.split("  #")[0].strip())
                if p is not None:
                    p["linha"], p["arq"] = frame.f_lineno, _rel(arq)
                    self.passos.append(p)
        return self._trace


def codigo_de_varios(funcoes):
    """Como codigo_de, com o arquivo de cada linha (números de linha se repetem entre arquivos)."""
    linhas = []
    for f in funcoes:
        arq = _rel(inspect.getsourcefile(f))
        linhas.append([None, f"# {arq}", arq])
        linhas += [[n, t, arq] for n, t in codigo_de([f]) if n is not None]
    return linhas


def gravar_fase2():
    from estruturas import fila as m_fila, pilha as m_pilha, lista_ligada as m_lista
    from jogo import fase2 as m_f2
    f = m_f2.Fase2()
    JOGADAS = ["aceitar", "guardar", "aceitar", "arquivar", "aceitar", "desfazer", "aceitar", "liberar", "arquivar", "aceitar"]
    atual = {"j": "", "n": 0}
    PERMITIDAS = {"executar", "validar", "desfazer", "regra_aceitar", "regra_guardar", "regra_arquivar", "regra_liberar",
                  "dequeue", "push", "pop", "peek", "inserir_fim"}
    PULAR_SE_DENTRO = {"_restaurar", "estado", "venceu"}

    def anotar(frame, linha, texto):
        fn = frame.f_code.co_name
        if fn not in PERMITIDAS:
            return None
        g = frame.f_back
        while g is not None:
            if g.f_code.co_name in PULAR_SE_DENTRO:
                return None
            g = g.f_back
        L = _locais(frame)
        eu = L.get("self")
        quem = ("a fila de chegada" if eu is f.fila else "a pilha de espera" if eu is f.pilha
                else "a pilha do Desfazer" if eu is f.historico else "a lista de custódia" if eu is f.custodia else "")
        onde = set(f.fila.para_lista()) | set(f.pilha.para_lista()) | set(f.custodia.percorrer()) | set(f.arquivo)
        passo = {"triagem": {"fila": f.fila.para_lista(), "pilha": f.pilha.para_lista(), "custodia": f.custodia.percorrer(),
                             "arquivo": list(f.arquivo), "historico": len(f.historico), "alvo": list(f.alvo),
                             "transito": [x for x in f.entrada if x not in onde]},   # já saiu de uma estrutura e ainda não entrou na outra
                 "jogada": atual["j"], "cont": [atual["n"], len(f.historico)], "did": "", "tec": ""}
        acao, e, frente, topo = L.get("acao"), L.get("e"), None, None
        ok_f, frente = f.fila.peek()
        ok_p, topo = f.pilha.peek()
        t = texto
        # ----- jogo/fase2.py -----
        if fn == "executar":
            if t.startswith("ok, motivo = self.validar(acao)"):
                passo["did"] = f"Jogada pedida: {acao}. Antes de mexer em qualquer coisa, confere se ela é permitida agora."
                passo["tec"] = f"validar('{acao}')"
            elif t.startswith("if not ok:"):
                ok = L.get("ok")
                passo["did"] = "A jogada é permitida? " + ("Sim." if ok else "Não.")
                passo["tec"] = f"ok = {ok}"
            elif t.startswith("return False, \"Movimento recusado"):
                passo["did"] = f"Jogada recusada: {L.get('motivo')} Nada foi alterado."
                passo["tec"] = "return False (estado intacto)"
            elif t.startswith("self.historico.push(self.estado())"):
                passo["did"] = "Antes de mudar o jogo, tira uma 'foto' do estado e guarda na pilha do Desfazer."
                passo["tec"] = "historico.push(estado())"
            elif t.startswith("_, e = self.fila.dequeue()"):
                passo["did"] = f"Tira {frente} da frente da fila de chegada."
                passo["tec"] = "e ← fila.dequeue()"
            elif t.startswith("_, e = self.pilha.pop()"):
                passo["did"] = f"Tira {topo} do topo da pilha de espera."
                passo["tec"] = "e ← pilha.pop()"
            elif t.startswith("self.custodia.inserir_fim(e)"):
                passo["did"] = f"Liga {e} no fim da lista de custódia."
                passo["tec"] = f"custodia.inserir_fim('{e}')"
            elif t.startswith("self.pilha.push(e)"):
                passo["did"] = f"Põe {e} no topo da pilha de espera: ele vai esperar a vez dele."
                passo["tec"] = f"pilha.push('{e}')"
            elif t.startswith("self.arquivo.append(e)"):
                passo["did"] = f"{e} não faz parte da custódia: vai para o arquivo morto."
                passo["tec"] = f"arquivo.append('{e}')"
            elif t.startswith("if self.venceu()"):
                passo["did"] = "A custódia está completa, na ordem E2 → E4 → E1 → E6?"
                passo["tec"] = "venceu()?"
            else:
                return None
        elif fn == "validar":
            if t.startswith("ok, frente = self.fila.peek()"):
                passo["did"] = "Olha quem está na frente da fila, sem tirar ninguém."
                passo["tec"] = "fila.peek()"
            elif t.startswith("ok, topo = self.pilha.peek()"):
                passo["did"] = "Olha quem está no topo da pilha, sem tirar ninguém."
                passo["tec"] = "pilha.peek()"
            elif t.startswith("return regra_"):
                regra = t.split("return ")[1].split("(")[0]
                passo["did"] = {"regra_aceitar": "Aplica a regra R1 (pôr na custódia).", "regra_guardar": "Aplica a regra R2 (guardar na pilha).",
                                "regra_arquivar": "Aplica a regra R3 (descartar no arquivo).", "regra_liberar": "Aplica a regra R4 (tirar da pilha para a custódia)."}[regra]
                passo["tec"] = t.replace("return ", "")
            else:
                return None
        elif fn.startswith("regra_"):
            if t.startswith("esperado = proximo_esperado"):
                passo["did"] = f"Qual prova a custódia espera agora? A ordem é {' → '.join(f.alvo)}."
                passo["tec"] = "esperado = próximo da ordem"
            elif t.startswith("if evidencia == esperado"):
                ev, es = L.get("evidencia"), L.get("esperado")
                passo["did"] = f"A prova da frente ({ev}) é a esperada ({es})? " + ("Sim." if ev == es else "Não.")
                passo["tec"] = f"{ev} == {es}?"
            elif t.startswith("if topo == esperado"):
                passo["did"] = f"O topo da pilha ({L.get('topo')}) é a prova esperada ({L.get('esperado')})?"
                passo["tec"] = f"{L.get('topo')} == {L.get('esperado')}?"
            elif t.startswith("if evidencia not in alvo") or t.startswith("if evidencia in alvo"):
                ev = L.get("evidencia")
                passo["did"] = f"{ev} faz parte da custódia? " + ("Sim." if ev in f.alvo else "Não: é cópia ou rascunho.")
                passo["tec"] = f"{ev} in alvo? {ev in f.alvo}"
            elif t.startswith("return True"):
                passo["did"] = "Regra cumprida: a jogada pode ser feita."
                passo["tec"] = "return True"
            elif t.startswith("return False"):
                passo["did"] = "Regra não cumprida: a jogada vai ser recusada, com o motivo."
                passo["tec"] = "return False, motivo"
            else:
                return None
        elif fn == "desfazer":
            if t.startswith("ok, anterior = self.historico.pop()"):
                passo["did"] = "Desfazer: tira a foto mais recente da pilha do Desfazer (a última que entrou é a primeira que sai)."
                passo["tec"] = "anterior ← historico.pop()"
            elif t.startswith("self._restaurar(anterior)"):
                passo["did"] = "Volta o jogo inteiro para essa foto: fila, pilha e custódia como estavam antes da última jogada."
                passo["tec"] = "_restaurar(anterior)"
            else:
                return None
        # ----- estruturas -----
        elif fn == "dequeue":
            if t.startswith("i = self.inicio.chave"):
                passo["did"] = f"Pega o valor do primeiro nó da fila: {eu.inicio.chave}."
            elif t.startswith("self.inicio = self.inicio.prox"):
                passo["did"] = "O início da fila passa a ser o nó seguinte: o primeiro saiu (FIFO)."
            elif t.startswith("if self.inicio is None:") and L.get("i") is not None:
                passo["did"] = "A fila ficou vazia? Se sim, o final também passa a ser vazio."
            else:
                return None
            passo["tec"] = t
        elif fn in ("push", "pop", "peek") and quem and eu is not f.fila:
            if fn == "push" and t.startswith("x.prox = self.topo"):
                passo["did"] = f"Em {quem}: o novo nó aponta para o antigo topo."
            elif fn == "push" and t.startswith("self.topo = x"):
                passo["did"] = f"Em {quem}: o novo nó vira o topo."
            elif fn == "pop" and t.startswith("t = self.topo.chave"):
                passo["did"] = f"Em {quem}: pega o valor do topo."
            elif fn == "pop" and t.startswith("self.topo = self.topo.prox"):
                passo["did"] = f"Em {quem}: o topo passa a ser o nó de baixo. O último que entrou saiu primeiro (LIFO)."
            elif fn == "peek" and t.startswith("return True, self.topo.chave"):
                passo["did"] = f"Em {quem}: o topo é {eu.topo.chave}."
            elif fn == "peek" and t.startswith("return False, None"):
                passo["did"] = f"{quem.capitalize()} está vazia."
            else:
                return None
            passo["tec"] = t
        elif fn == "peek":
            if t.startswith("return True, self.inicio.chave"):
                passo["did"] = f"A frente da fila é {eu.inicio.chave}."
            elif t.startswith("return False, None"):
                passo["did"] = "A fila está vazia."
            else:
                return None
            passo["tec"] = t
        elif fn == "inserir_fim":
            if t.startswith("x = No(chave)"):
                passo["did"] = f"Cria um nó novo para {L.get('chave')}."
            elif t.startswith("if self.ultimo is None"):
                passo["did"] = "A custódia está vazia? Se sim, o nó entra logo depois do nó cabeça."
            elif t.startswith("self.cabeca.prox = x"):
                passo["did"] = "O nó cabeça passa a apontar para o novo nó: ele é o primeiro da custódia."
            elif t.startswith("self.ultimo.prox = x"):
                passo["did"] = f"O último nó ({eu.ultimo.chave}) passa a apontar para o novo: a corrente cresce no fim."
            elif t.startswith("self.ultimo = x"):
                passo["did"] = "Atualiza o ponteiro do último nó, para a próxima inserção ser direta (O(1))."
            else:
                return None
            passo["tec"] = t
        else:
            return None
        return passo

    def partida():
        for j in JOGADAS:
            atual["n"] += 1
            atual["j"] = f"Jogada {atual['n']}: " + {"aceitar": "Pôr na custódia", "guardar": "Guardar na pilha", "arquivar": "Descartar",
                                                       "liberar": "Tirar da pilha", "desfazer": "Desfazer"}[j]
            if j == "desfazer":
                f.desfazer()
            else:
                f.executar(j)

    tr = RastreadorVarios([m_f2.__file__, m_fila.__file__, m_pilha.__file__, m_lista.__file__], anotar, max_passos=500)
    tr.rodar(partida)
    tr.passos.append({"linha": None, "fim": True, "jogada": "Fim da partida",
                      "triagem": {"fila": f.fila.para_lista(), "pilha": f.pilha.para_lista(), "custodia": f.custodia.percorrer(),
                                  "arquivo": list(f.arquivo), "historico": len(f.historico), "alvo": list(f.alvo)},
                      "cont": [len(JOGADAS), len(f.historico)],
                      "did": f"Custódia completa: {' → '.join(f.custodia.percorrer())}. Foram {len(JOGADAS)} jogadas, contando uma recusada e um Desfazer.",
                      "tec": "venceu() = " + str(f.venceu())})
    F2, Fi, Pi, Li = m_f2.Fase2, m_fila.Fila, m_pilha.Pilha, m_lista.ListaLigada
    return {"varios": True, "passos": tr.passos, "rotulos": ["Jogada", "Fotos na pilha do Desfazer"],
            "codigo": codigo_de_varios([F2.executar, F2.validar, F2.desfazer, m_f2.regra_aceitar, m_f2.regra_guardar,
                                        m_f2.regra_arquivar, m_f2.regra_liberar, Fi.dequeue, Fi.peek, Pi.push, Pi.pop, Pi.peek, Li.inserir_fim]),
            "arquivo": "jogo/fase2.py e estruturas/",
            "nota": "Uma partida curta: uma jogada recusada, a solução e um Desfazer no meio. Cada operação na fila, na pilha e na lista ligada é a do código real."}


def dados_motor_fase2():
    return {"algoritmos": {"triagem": gravar_fase2()}}
