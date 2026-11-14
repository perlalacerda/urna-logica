"""
Gera visualizacao.html: UMA página autocontida, que funciona SEM internet.

Como funciona:
    1. O Python roda os algoritmos de verdade (os mesmos do jogo) e guarda
       cada passo: a fila/pilha da busca, o vetor durante a ordenação, a AVL
       antes e depois de cada inserção, as estruturas da Fase 2.
    2. Esses passos viram dados (JSON) embutidos no HTML.
    3. Um pequeno JavaScript desenha cada passo e permite avançar, voltar
       ou "tocar" a animação.
Nada é inventado na página: tudo vem da execução real do código Python.

Abas:
    Mapa e busca  | Árvore de busca | AVL | Triagem (Fase 2) | Ordenação | Métricas
"""

import json
import os

from algoritmos.ordenacao import bubble_sort, merge_sort, quick_sort
from algoritmos.solver import bfs, dfs_recursiva, dfs_pilha
from estruturas.avl import fator_balanceamento
from jogo.fase2 import Fase2, ProblemaTriagem
from jogo.fase3 import ProblemaMapa, construir_mapa, LOCAIS, PISTAS, PORTAS, ARESTAS
from jogo.fase4 import Fase4, OPCOES_ROTACAO
from jogo.cenarios import cenarios_de_comparacao
from jogo.fase5 import Fase5
from jogo import narrativa

# posições dos locais no desenho (escolhidas à mão para não haver cruzamentos)
POSICOES = {"A": (90, 235), "B": (230, 130), "C": (230, 340), "E": (230, 450),
            "I": (360, 235), "H": (490, 130), "G": (490, 340), "D": (650, 130), "F": (650, 340)}


# ------------------------------------------------------------ mapa e busca
def rotulo_curto(e):
    pos, pistas, portas, energia = e
    return f"{pos} {{{','.join(pistas)}}}" + (f" p:{','.join(portas)}" if portas else "") + f" e{energia}"


def dados_busca():
    G = construir_mapa()
    mapa = {
        "vertices": [{"id": v, "nome": LOCAIS[v], "x": POSICOES[v][0], "y": POSICOES[v][1],
                      "pista": PISTAS.get(v), "porta": PORTAS.get(v)} for v in G.vertices()],
        "arestas": [list(a) for a in ARESTAS],
        "adjacencia": {v: G.vizinhos(v) for v in G.vertices()},
    }
    from algoritmos.busca_grafo import bfs as bfs_grafo
    d, pi, ordem, _ = bfs_grafo(G, "A")
    mapa["camadas"] = {v: d[v] for v in G.vertices()}        # distância (em corredores) a partir de A
    mapa["ordem_bfs"] = ordem
    mapa["pi"] = pi
    estrategias = {}
    for nome, alg, tipo in (("BFS", bfs, "FILA"), ("DFS recursiva", dfs_recursiva, "PILHA DE CHAMADAS"),
                            ("DFS com pilha", dfs_pilha, "PILHA")):
        r = alg(ProblemaMapa(G))
        visitados_ate_agora, quadros = [], []
        for u, fronteira in r.passos:
            visitados_ate_agora.append(u[0])
            quadros.append({"atual": rotulo_curto(u), "pos": u[0],
                            "fronteira": [rotulo_curto(e) for e in fronteira],
                            "visitados": list(visitados_ate_agora)})
        estrategias[nome] = {
            "tipo_fronteira": tipo, "quadros": quadros,
            "caminho": [e[0] for _, e in r.caminho],
            "caminho_estados": [rotulo_curto(e) for _, e in r.caminho],
            "resumo": {"acoes": r.numero_acoes(), "expandidos": r.expandidos, "gerados": r.gerados,
                       "repetidos": r.repetidos, "fronteira": r.maior_fronteira,
                       "avl_nos": r.avl_nos, "avl_altura": r.avl_altura},
            "arvore": layout_arvore_busca(r),
        }
    return {"mapa": mapa, "estrategias": estrategias}


def layout_arvore_busca(r, rotulo=None):
    rotulo = rotulo or rotulo_curto
    """Posiciona a árvore de busca: x pela ordem das folhas, y pela profundidade."""
    if not r.ordem:
        return {"nos": [], "arestas": []}
    filhos = {}
    for pai, acao, filho in r.arvore:
        filhos.setdefault(pai, []).append(filho)
    no_caminho = {e for _, e in r.caminho}
    nos, arestas, proxima_folha = {}, [], [0]

    def posiciona(e, prof):
        lista = filhos.get(e, [])
        if not lista:
            x = proxima_folha[0]
            proxima_folha[0] += 1
        else:
            xs = [posiciona(f, prof + 1) for f in lista]
            x = (xs[0] + xs[-1]) / 2
            for f in lista:
                arestas.append([id(e), id(f)])
        nos[id(e)] = {"id": id(e), "x": x, "y": prof, "rotulo": rotulo(e),
                      "caminho": e in no_caminho}
        return x

    posiciona(r.ordem[0], 0)
    return {"nos": list(nos.values()), "arestas": arestas}


# ------------------------------------------------------------ AVL
def arvore_para_dict(r):
    if r is None:
        return None
    return {"k": r.chave, "h": r.h, "fb": fator_balanceamento(r),
            "e": arvore_para_dict(r.esq), "d": arvore_para_dict(r.dir)}


def dados_avl():
    f = Fase4()
    quadros = []
    for _ in f.sequencia:
        antes = arvore_para_dict(f.avl.raiz)
        r = f.inserir_proximo("nenhuma")
        quadros.append({"codigo": r["codigo"], "rotacao": r["ocorrido"], "no": r["no"],
                        "explicacao": r["explicacao"], "antes": antes,
                        "depois": arvore_para_dict(f.avl.raiz), "altura": r["altura"]})
    return {"sequencia": list(f.sequencia), "quadros": quadros, "opcoes": list(OPCOES_ROTACAO)}


# ------------------------------------------------------------ Fase 2
def dados_triagem():
    r = bfs(ProblemaTriagem())
    f = Fase2()
    quadros = [{"acao": "início", "msg": "Seis evidências chegaram, nesta ordem, à fila de entrada.",
                "fila": f.fila.para_lista(), "pilha": f.pilha.para_lista(),
                "custodia": f.custodia.percorrer(), "arquivo": list(f.arquivo)}]
    for acao, _ in r.caminho[1:]:
        ok, msg = f.executar(acao)
        quadros.append({"acao": acao, "msg": msg, "fila": f.fila.para_lista(),
                        "pilha": f.pilha.para_lista(), "custodia": f.custodia.percorrer(),
                        "arquivo": list(f.arquivo)})
    return {"alvo": list(f.alvo), "quadros": quadros}


# ------------------------------------------------------------ ordenação
class VetorRastreado(list):
    """Lista que tira uma "foto" a cada escrita A[i] = x (para animar)."""

    def __init__(self, dados):
        super().__init__(dados)
        self.fotos = [{"v": list(dados), "i": []}]

    def __setitem__(self, i, valor):
        super().__setitem__(i, valor)
        self.fotos.append({"v": list(self), "i": [i]})


def dados_ordenacao():
    exemplo = [12, 35, 87, 26, 9, 28, 7]        # exemplo do Merge Sort da aula 02, slide 22
    res = {}
    for nome, alg in (("Bubble Sort", bubble_sort), ("Merge Sort", merge_sort), ("Quick Sort", quick_sort)):
        A = VetorRastreado(exemplo)
        c = alg(A)
        res[nome] = {"fotos": A.fotos, "comparacoes": c.comparacoes, "movimentacoes": c.movimentacoes}
    return {"entrada": exemplo, "algoritmos": res}


# ------------------------------------------------------------ métricas
def dados_metricas():
    linhas = []
    for nome, p in cenarios_de_comparacao():
        for alg in (bfs, dfs_recursiva, dfs_pilha):
            r = alg(p)
            linhas.append({"cenario": nome, "estrategia": r.algoritmo, "acoes": r.numero_acoes(),
                           "expandidos": r.expandidos, "gerados": r.gerados, "repetidos": r.repetidos,
                           "fronteira": r.maior_fronteira})
    return linhas


# ------------------------------------------------------------ narrativa e auditoria
def dados_narrativa():
    return {"titulo": narrativa.TITULO, "prologo": narrativa.PROLOGO, "aviso": narrativa.AVISO,
            "capitulos": narrativa.CAPITULOS, "epilogo": narrativa.EPILOGO}


def dados_auditoria():
    """Executa a Fase 5 de verdade (solver resolve as etapas) e devolve o relatório."""
    f = Fase5()
    f.etapa_lote(algoritmo="merge")
    f.etapa_triagem()
    f.etapa_mapa()
    f.comparar_estrategias()
    etapas = []
    for chave, nome in (("lote", "Etapa 1 — Lote de registros"), ("triagem", "Etapa 2 — Central de Triagem"),
                        ("mapa", "Etapa 3 — Mapa das Seções")):
        e = f.etapas[chave]
        etapas.append({"nome": nome, "ok": e["ok"], "detalhe": e["detalhe"],
                       "origem": e.get("origem", ""), "checagens": [[d, ok] for d, ok in e["checagens"]]})
    return {"etapas": etapas, "consistente": f.consistente()}


# ------------------------------------------------------------ audiência: dados extras
def dados_lote():
    """Fase 1: o lote real, os quadros da ordenação (com registros) e o pedaço do enigma."""
    from jogo.fase1 import Fase1
    from jogo.registros import CRITERIOS
    f = Fase1()
    def reg(r):
        return {"id": r.id_registro, "zona": r.zona, "secao": r.secao, "opcao": r.opcao,
                "hora": r.timestamp, "status": r.status}
    embaralhado = [reg(r) for r in f.registros]
    # par para o "sua vez": mesmo horário, zonas diferentes
    par = None
    for a in f.registros:
        for b in f.registros:
            if a.timestamp == b.timestamp and a.zona != b.zona and a.id_registro < b.id_registro:
                par = (a, b)
                break
        if par:
            break
    chave = CRITERIOS["auditoria"]
    primeiro = min(par, key=chave)
    # recusa ao ordenar só pelo horário (mensagem real do jogo)
    tentativa = Fase1()
    recusa = tentativa.ordenar("merge", "horario")
    algs = {}
    for nome, fn in (("Bubble Sort", bubble_sort), ("Merge Sort", merge_sort), ("Quick Sort", quick_sort)):
        g = Fase1()
        A = VetorRastreado(list(g.registros))
        c = fn(A, chave)
        # Mostra só os instantes em que o vetor é uma permutação completa (cada ficha uma vez):
        # no meio de uma troca a mesma ficha aparece duas vezes, o que confunde o público.
        quadros, mudou = [], set()
        for foto in A.fotos:
            ids = [r.id_registro for r in foto["v"]]
            mudou.update(foto["i"])
            if len(set(ids)) == len(ids):
                quadros.append({"ids": ids, "i": sorted(mudou)})
                mudou = set()
        algs[nome] = {"quadros": quadros,
                      "comparacoes": c.comparacoes, "movimentacoes": c.movimentacoes}
    comparacao = [{"n": n, "alg": a, "comp": comp, "mov": mov}
                  for n, a, comp, mov, _ in Fase1().comparar_algoritmos(tamanhos=(12, 100, 500))]
    return {"registros": {r["id"]: r for r in embaralhado}, "embaralhado": [r["id"] for r in embaralhado],
            "par": [reg(par[0]), reg(par[1])], "par_primeiro": primeiro.id_registro,
            "recusa": recusa["mensagem"], "algoritmos": algs, "comparacao": comparacao,
            "enigma": Fase1.ENIGMA}


def dados_triagem_jogavel():
    """
    Fase 2 inteira: TODOS os estados alcançáveis (são só 14) e, para cada um,
    o resultado das 4 ações calculado pelas regras do Python. A página só
    consulta esta tabela — não tem regras próprias.
    """
    from collections import deque
    inicial = Fase2().estado()
    ids, ordem, fila = {inicial: 0}, [inicial], deque([inicial])
    while fila:
        e = fila.popleft()
        for _, novo in Fase2.a_partir_do_estado(e).sucessores():
            if novo not in ids:
                ids[novo] = len(ordem)
                ordem.append(novo)
                fila.append(novo)
    estados = []
    for e in ordem:
        f = Fase2.a_partir_do_estado(e)
        acoes = {}
        for acao in Fase2.ACOES:
            g = Fase2.a_partir_do_estado(e)
            ok, msg = g.executar(acao)
            acoes[acao] = {"ok": ok, "msg": msg, "destino": ids[g.estado()] if ok else None}
        estados.append({"fila": list(e[0]), "pilha": list(e[1]), "custodia": list(e[2]),
                        "arquivo": f.arquivo, "venceu": f.venceu(), "acoes": acoes})
    return {"estados": estados, "alvo": list(Fase2().alvo)}


def dados_mapa_jogavel():
    """Fase 3: todos os estados alcançáveis e o resultado de cada movimento (regras do Python)."""
    from collections import deque
    from jogo.fase3 import mover, estado_inicial, DESTINO
    G = construir_mapa()
    inicial = estado_inicial()
    ids, ordem, fila = {inicial: 0}, [inicial], deque([inicial])
    while fila:
        e = fila.popleft()
        for v in G.vizinhos(e[0]):
            ok, novo, _ = mover(G, e, v)
            if ok and novo not in ids:
                ids[novo] = len(ordem)
                ordem.append(novo)
                fila.append(novo)
    estados = []
    for e in ordem:
        movs = {}
        for v in G.vizinhos(e[0]):              # não vizinhos: a página só diz "não há corredor"
            ok, novo, msg = mover(G, e, v)
            movs[v] = {"ok": ok, "msg": msg, "destino": ids[novo] if ok else None}
        estados.append({"pos": e[0], "pistas": list(e[1]), "portas": list(e[2]), "energia": e[3],
                        "venceu": e[0] == DESTINO, "movs": movs})
    return {"estados": estados, "adjacencia": {v: G.vizinhos(v) for v in G.vertices()}}


def dados_pares():
    from jogo.fase4 import PARES_ESTADOS, resposta_correta, explicar
    from jogo.fase3 import rotulo
    return [{"visto": rotulo(a), "novo": rotulo(b), "resposta": list(resposta_correta(a, b)),
             "explicacao": explicar(a, b)} for a, b in PARES_ESTADOS]


# ------------------------------------------------------------ página
def gerar_html(caminho="visualizacao.html"):
    dados = {"busca": dados_busca(), "avl": dados_avl(), "triagem": dados_triagem(),
             "ordenacao": dados_ordenacao(), "metricas": dados_metricas(),
             "narrativa": dados_narrativa(), "auditoria": dados_auditoria(),
             "lote": dados_lote(), "triagem_jogavel": dados_triagem_jogavel(),
             "mapa_jogavel": dados_mapa_jogavel(), "pares": dados_pares()}
    modelo_path = os.path.join(os.path.dirname(__file__), "visualizacao_modelo.html")
    with open(modelo_path, encoding="utf-8") as arq:
        modelo = arq.read()
    html = modelo.replace("/*__DADOS__*/null", json.dumps(dados, ensure_ascii=False))
    with open(caminho, "w", encoding="utf-8") as arq:
        arq.write(html)
    return os.path.abspath(caminho)


if __name__ == "__main__":
    print(gerar_html())
