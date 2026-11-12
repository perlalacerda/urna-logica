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


def layout_arvore_busca(r):
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
        nos[id(e)] = {"id": id(e), "x": x, "y": prof, "rotulo": rotulo_curto(e),
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


# ------------------------------------------------------------ página
def gerar_html(caminho="visualizacao.html"):
    dados = {"busca": dados_busca(), "avl": dados_avl(), "triagem": dados_triagem(),
             "ordenacao": dados_ordenacao(), "metricas": dados_metricas(),
             "narrativa": dados_narrativa(), "auditoria": dados_auditoria()}
    modelo_path = os.path.join(os.path.dirname(__file__), "visualizacao_modelo.html")
    with open(modelo_path, encoding="utf-8") as arq:
        modelo = arq.read()
    html = modelo.replace("/*__DADOS__*/null", json.dumps(dados, ensure_ascii=False))
    with open(caminho, "w", encoding="utf-8") as arq:
        arq.write(html)
    return os.path.abspath(caminho)


if __name__ == "__main__":
    print(gerar_html())
