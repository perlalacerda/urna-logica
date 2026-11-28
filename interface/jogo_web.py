"""
Gera jogo.html: o jogo completo no navegador, sem internet.

Como funciona (e por que a página NÃO tem regras próprias):
    1. Este módulo executa as REGRAS REAIS do jogo (jogo/fase1..fase5.py)
       e calcula, para cada fase, todas as situações possíveis e o
       resultado de cada jogada (aceita ou recusada, com a mensagem).
    2. Para cada situação das Fases 2 e 3, o SOLVER (BFS) calcula a dica:
       o próximo passo do caminho mais curto até o objetivo.
    3. Tudo vira dados (JSON) dentro de um único arquivo HTML.
    4. O JavaScript da página só CONSULTA essas tabelas e desenha a tela.
Assim, o que a professora joga no navegador é decidido pelo mesmo código
Python que ela lê no repositório. O teste testes/test_jogo_web.py confere.

Uso:   py -m interface.jogo_web     (gera e mostra o caminho de jogo.html)
"""

import json
import os
from collections import deque

from algoritmos.solver import bfs, dfs_recursiva, dfs_pilha
from algoritmos.ordenacao import ALGORITMOS
from jogo import narrativa
from jogo.dicas import _TriagemDaqui, _MapaDaqui, orientacao_fase3
from jogo.fase1 import Fase1
from jogo.fase2 import Fase2, EVIDENCIAS, ProblemaTriagem, proximo_esperado
from jogo.fase3 import (Fase3, ProblemaMapa, construir_mapa, mover, estado_inicial,
                        LOCAIS, PISTAS, PORTAS, ARESTAS, DESTINO)
from jogo.fase4 import Fase4, PARES_ESTADOS, resposta_correta, explicar, OPCOES_ROTACAO
from jogo.fase5 import Fase5
from jogo.mapa_custos import (FaseMapaCustos, construir_mapa_custos, comparar as comparar_custos,
                              dijkstra_grafo_puro, avaliar_chegada, PESOS, ENERGIA_CUSTOS)
from jogo.dicas import dica_mapa_custos, orientacao_mapa_custos
from jogo.registros import CRITERIOS, DESCRICAO_CRITERIOS, CAMPOS, NOMES_CAMPOS, chave_composta
from interface.visualizacao import POSICOES, arvore_para_dict, layout_arvore_busca

ROTULO_ACAO = {"aceitar": "Aceitar", "guardar": "Guardar", "arquivar": "Arquivar", "liberar": "Liberar"}


# ============================================================ FASE 1
def dados_fase1():
    """Resultado de cada combinação algoritmo × critério, calculado por Fase1.ordenar."""
    base = Fase1()
    reg = lambda r: [r.id_registro, r.zona, r.secao, r.opcao, r.timestamp, r.status]
    resultados = {}
    for alg in ALGORITMOS:
        for crit in CRITERIOS:
            f = Fase1()
            res = f.ordenar(alg, crit)
            c = res["contador"]
            resultados[f"{alg}|{crit}"] = {
                "registros": [reg(r) for r in f.registros], "aceito": res["aceito"],
                "erro": res["posicao_erro"], "mensagem": res["mensagem"],
                "algoritmo": c.algoritmo, "comparacoes": c.comparacoes, "movimentacoes": c.movimentacoes}
    comparacao = [[n, a, comp, mov] for n, a, comp, mov, _ in base.comparar_algoritmos()]
    chaves = dados_chaves_fase1(base)
    cenarios = dados_cenarios_fase1(base.seed)
    return {"nome": Fase1.NOME, "abertura": Fase1.ABERTURA, "enigma": Fase1.ENIGMA,
            "registros": [reg(r) for r in base.registros],
            "criterios": [[c, DESCRICAO_CRITERIOS[c]] for c in ("id", "zona", "horario", "auditoria")],
            "algoritmos": [["bubble", "Bubble Sort"], ["merge", "Merge Sort"], ["quick", "Quick Sort"]],
            "resultados": resultados, "comparacao": comparacao, "chaves": chaves, "cenarios": cenarios,
            "campos": [[c, NOMES_CAMPOS[c]] for c in CAMPOS]}


def dados_cenarios_fase1(seed, n=500):
    """
    Quadro "O que aprendemos" da Fase 1: comparações de cada método com 500
    registros em três tipos de entrada (aleatória, já ordenada, invertida).
    Mesma montagem de experimentos.py: os números são medidos, não escritos à mão.
    """
    from algoritmos.ordenacao import ordenar
    from jogo.registros import gerar_registros, embaralhar
    chave = CRITERIOS["auditoria"]
    base = embaralhar(gerar_registros(n, seed), seed + 1)
    entradas = (("aleatoria", base), ("ordenada", sorted(base, key=chave)),
                ("invertida", sorted(base, key=chave, reverse=True)))
    return {"n": n, "linhas": {tipo: {alg: ordenar(list(dados), alg, chave).comparacoes
                                      for alg in ("bubble", "merge", "quick")}
                               for tipo, dados in entradas}}


def dados_chaves_fase1(base):
    """
    Para cada chave que a jogadora pode montar (1 a 4 peças, sem repetir) e cada
    método: o resultado de Fase1.ordenar e os quadros da animação.
    Cada quadro é a ordem das fichas, escrita como uma letra por ficha
    (posição da ficha no lote embaralhado, em base 36) — só os quadros em que o
    vetor é uma permutação completa, como na visualização.
    """
    from itertools import permutations
    from interface.visualizacao import VetorRastreado
    pos = {r.id_registro: i for i, r in enumerate(base.registros)}
    letra = "0123456789abcdefghijklmnopqrstuvwxyz"
    res = {}
    for n in range(1, len(CAMPOS) + 1):
        for campos in permutations(CAMPOS, n):
            for alg in ALGORITMOS:
                f = Fase1()
                r = f.ordenar(alg, campos)
                g = Fase1()
                A = VetorRastreado(list(g.registros))
                ALGORITMOS[alg](A, chave_composta(campos))
                quadros = []
                for foto in A.fotos:
                    ids = [x.id_registro for x in foto["v"]]
                    if len(set(ids)) == len(ids):
                        q = "".join(letra[pos[i]] for i in ids)
                        if not quadros or quadros[-1] != q:
                            quadros.append(q)
                c = r["contador"]
                res[f"{alg}|{'>'.join(campos)}"] = {
                    "aceito": r["aceito"], "erro": r["posicao_erro"], "mensagem": r["mensagem"],
                    "comparacoes": c.comparacoes, "movimentacoes": c.movimentacoes, "quadros": quadros}
    return res


# ============================================================ FASE 2
def dados_fase2():
    """Todas as situações da triagem, o resultado das 4 ações e a dica da BFS."""
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
        r = bfs(_TriagemDaqui(e, f.entrada, f.alvo))
        if f.venceu():
            dica = "Fase concluída."
        elif r.encontrou:
            dica = (f"O solver (BFS) sugere: {ROTULO_ACAO[r.caminho[1][0]]}. "
                    f"Pelo caminho mais curto faltam {r.numero_acoes()} ação(ões).")
        else:
            dica = "Desta situação não há como completar a custódia. Use Desfazer ou Recomeçar."
        esperado = proximo_esperado(e[2], f.alvo)
        estados.append({"fila": list(e[0]), "pilha": list(e[1]), "custodia": list(e[2]),
                        "arquivo": f.arquivo, "venceu": f.venceu(), "acoes": acoes,
                        "dica": dica, "esperado": esperado})
    return {"nome": Fase2.NOME, "abertura": Fase2.ABERTURA, "alvo": list(Fase2().alvo),
            "evidencias": EVIDENCIAS, "estados": estados,
            "minimo": bfs(ProblemaTriagem()).numero_acoes()}     # 3 estrelas = o mínimo da BFS


# ============================================================ FASE 3
def _para_web(texto):
    """Troca instruções de teclado por instruções de clique."""
    return (texto.replace(" Digite a letra de um vizinho (? = dica).", " Clique num local vizinho no mapa.")
                 .replace(" Digite a letra de um vizinho.", " Clique num local vizinho no mapa.")
                 .replace(" Volte (0) e escolha a próxima fase.", " Escolha a próxima fase no menu.")
                 .replace(" Desfaça (U) ou reinicie (R).", " Use Desfazer ou Recomeçar."))


class _EstadoFase3:
    """Objeto mínimo para reaproveitar dicas.orientacao_fase3 (que lê .estado e .venceu())."""

    def __init__(self, estado):
        self.estado = estado

    def venceu(self):
        return self.estado[0] == DESTINO


def dados_fase3():
    """Todas as situações do mapa, cada movimento possível e a dica da BFS."""
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
        for v in G.vizinhos(e[0]):
            ok, novo, msg = mover(G, e, v)
            movs[v] = {"ok": ok, "msg": msg, "destino": ids[novo] if ok else None}
        r = bfs(_MapaDaqui(e, G))
        if e[0] == DESTINO:
            dica = "Fase concluída."
        elif r.encontrou:
            p = r.caminho[1][1][0]
            dica = (f"O solver (BFS) sugere ir para {p} ({LOCAIS[p]}). "
                    f"Pelo caminho mais curto faltam {r.numero_acoes()} movimento(s).")
        else:
            dica = "Daqui não dá para chegar ao destino com a energia que resta. Use Desfazer ou Recomeçar."
        estados.append({"pos": e[0], "pistas": list(e[1]), "portas": list(e[2]), "energia": e[3],
                        "venceu": e[0] == DESTINO, "movs": movs, "dica": dica,
                        "orientacao": _para_web(orientacao_fase3(_EstadoFase3(e)))})
    f = Fase3()
    curto, _ = f.menor_caminho_ignorando_portas()
    return {"nome": Fase3.NOME, "abertura": Fase3.ABERTURA, "estados": estados,
            "vertices": [{"id": v, "nome": LOCAIS[v], "x": POSICOES[v][0], "y": POSICOES[v][1],
                          "pista": PISTAS.get(v), "porta": PORTAS.get(v)} for v in G.vertices()],
            "arestas": [list(a) for a in ARESTAS], "adjacencia": {v: G.vizinhos(v) for v in G.vertices()},
            "curto": curto, "minimo": bfs(ProblemaMapa()).numero_acoes()}     # 3 estrelas = o mínimo da BFS


# ============================================================ DESAFIO EXTRA: MAPA COM CUSTOS (aula 11)
class _SituacaoCustos:
    """Objeto mínimo para reaproveitar dica_mapa_custos e orientacao_mapa_custos."""

    def __init__(self, estado, G):
        self.estado, self.G = estado, G

    def venceu(self):
        return self.estado[0] == DESTINO


def dados_mapa_custos():
    """Mesma ideia da Fase 3: todas as situações, cada movimento, a dica (agora do Dijkstra)."""
    G = construir_mapa_custos()
    inicial = estado_inicial(ENERGIA_CUSTOS)
    ids, ordem, fila = {inicial: 0}, [inicial], deque([inicial])
    while fila:
        e = fila.popleft()
        for v in G.vizinhos(e[0]):
            ok, novo, _ = mover(G, e, v)
            if ok and novo not in ids:
                ids[novo] = len(ordem)
                ordem.append(novo)
                fila.append(novo)
    bfs_r, guloso_r, dij_r = comparar_custos()
    otimo = dij_r.custo
    sem_teclas = lambda t: _para_web(t).replace(" (U)", "").replace(" (R)", "").replace(" (T)", " (abaixo)")
    estados = []
    for e in ordem:
        movs = {}
        for v in G.vizinhos(e[0]):
            ok, novo, msg = mover(G, e, v)
            movs[v] = {"ok": ok, "msg": msg, "destino": ids[novo] if ok else None}
        sit = _SituacaoCustos(e, G)
        estados.append({"pos": e[0], "pistas": list(e[1]), "portas": list(e[2]), "energia": e[3],
                        "venceu": e[0] == DESTINO, "movs": movs, "dica": sem_teclas(dica_mapa_custos(sit)),
                        "orientacao": sem_teclas(orientacao_mapa_custos(sit)),
                        "avaliacao": avaliar_chegada(ENERGIA_CUSTOS - e[3], otimo) if e[0] == DESTINO else ""})
    d, _, S, passos, cam = dijkstra_grafo_puro()
    resumo = lambda r: {"algoritmo": r.algoritmo, "encontrou": r.encontrou, "acoes": r.numero_acoes(),
                        "custo": r.custo, "expandidos": r.expandidos, "fronteira": r.maior_fronteira,
                        "caminho": [e[0] for _, e in r.caminho]}
    return {"nome": FaseMapaCustos.NOME, "abertura": FaseMapaCustos.ABERTURA, "energia": ENERGIA_CUSTOS,
            "estados": estados, "otimo": otimo,
            "pesos": {f"{u}-{v}": w for (u, v), w in PESOS.items()},
            "adjacencia": {v: G.vizinhos(v) for v in G.vertices()},
            "comparacao": [resumo(r) for r in (bfs_r, guloso_r, dij_r)],
            "puro": {"ordem": S, "d": {v: d[v] for v in S}, "caminho": cam,
                     "passos": [{"extraiu": p["extraiu"], "d": p["d"],
                                 "melhorou": [[v, (None if a == float("inf") else a), b] for v, a, b in p["melhorou"]],
                                 "heap": [[v, None if x == float("inf") else x] for v, x in p["heap"]]} for p in passos]}}


# ============================================================ FASE 4
def dados_fase4():
    f = Fase4()
    lacres = []
    for _ in f.sequencia:
        antes = arvore_para_dict(f.avl.raiz)
        r = f.inserir_proximo("nenhuma")
        lacres.append({"codigo": r["codigo"], "rotacao": r["ocorrido"], "explicacao": r["explicacao"],
                       "antes": antes, "depois": arvore_para_dict(f.avl.raiz), "altura": r["altura"]})
    consultas = {}
    for k in range(0, 101):                    # busca de qualquer código de 0 a 100 na árvore final
        achou, caminho, comps = f.consultar(k)
        consultas[k] = {"achou": achou, "caminho": caminho, "comparacoes": comps}
    from jogo.fase3 import rotulo
    sit = lambda e: {"pos": e[0], "local": LOCAIS[e[0]], "pistas": list(e[1]), "portas": list(e[2]), "energia": e[3]}
    pares = [{"visto": rotulo(a), "novo": rotulo(b), "a": sit(a), "b": sit(b), "resposta": list(resposta_correta(a, b)),
              "explicacao": explicar(a, b)} for a, b in PARES_ESTADOS]
    return {"nome": Fase4.NOME, "abertura": Fase4.ABERTURA, "lacres": lacres, "opcoes": list(OPCOES_ROTACAO),
            "pares": pares, "consultas": consultas, "altura_final": f.avl.altura()}


# ============================================================ FASE 5 e solver
def dados_fase5():
    """Etapa do lote por algoritmo, solução do solver para triagem e mapa, comparação BFS × DFS."""
    lotes = {}
    for alg in ALGORITMOS:
        f = Fase5()
        e = f.etapa_lote(algoritmo=alg)
        lotes[alg] = {"ok": e["ok"], "detalhe": e["detalhe"], "checagens": e["checagens"]}
    f = Fase5()
    f.etapa_triagem()
    f.etapa_mapa()
    linhas = f.comparar_estrategias()
    return {"nome": Fase5.NOME, "abertura": Fase5.ABERTURA, "lotes": lotes,
            "triagem_solver": f.etapas["triagem"], "mapa_solver": f.etapas["mapa"],
            "comparacao": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items()} for x in linhas],
            "epilogo": narrativa.EPILOGO}


def _rotulo_triagem(e):
    return f"fila[{' '.join(e[0])}] pilha[{' '.join(e[1])}] custódia[{' '.join(e[2])}]"


def _rotulo_mapa(e):
    return f"{e[0]} {{{','.join(e[1])}}}" + (f" p:{','.join(e[2])}" if e[2] else "") + f" e{e[3]}"


def dados_solver():
    res = {}
    for chave, problema, rot in (("triagem", ProblemaTriagem(), _rotulo_triagem),
                                 ("mapa", ProblemaMapa(), _rotulo_mapa)):
        res[chave] = {}
        for alg in (bfs, dfs_recursiva, dfs_pilha):
            r = alg(problema)
            arv = layout_arvore_busca(r, rot)
            nos = arv["nos"]
            res[chave][r.algoritmo] = {
                "encontrou": r.encontrou, "acoes": r.numero_acoes(), "custo": r.custo,
                "caminho": [[a or "início", rot(e)] for a, e in r.caminho],
                "expandidos": r.expandidos, "gerados": r.gerados, "repetidos": r.repetidos,
                "fronteira": r.maior_fronteira, "avl_nos": r.avl_nos, "avl_altura": r.avl_altura,
                "avl_rotacoes": r.avl_rotacoes, "tempo_ms": round(r.tempo_ms, 3),
                "arvore": {"nos": nos, "arestas": arv["arestas"]}}
    return res


# ============================================================ "VER O CÓDIGO DESTA FASE"
# Para cada fase: as funções que fazem o trabalho, com a aula de origem. O texto do
# código é copiado do arquivo AGORA (inspect), por isso a página nunca mostra uma
# versão velha. O número da linha é o mesmo da matriz de inspeção.
CODIGO_POR_FASE = {
    "f1": [("jogo.registros:chave_composta", "Chave composta (enunciado, Fase 1)"),
           ("algoritmos.ordenacao:bubble_sort", "Bubble Sort — aula 02, slide 10"),
           ("algoritmos.ordenacao:merge_sort", "Merge Sort — aula 02, slides 20–22"),
           ("algoritmos.ordenacao:quick_sort", "Quick Sort — aula 04, slides 31–37"),
           ("algoritmos.ordenacao:_particiona", "Partição de Lomuto — aula 04")],
    "f2": [("estruturas.fila:Fila.dequeue", "Fila: remover do início — aula 06"),
           ("estruturas.pilha:Pilha.push", "Pilha: empilhar — aula 06"),
           ("estruturas.pilha:Pilha.pop", "Pilha: desempilhar — aula 06"),
           ("estruturas.lista_ligada:ListaLigada.inserir_fim", "Lista ligada: inserir no fim — aula 06"),
           ("jogo.fase2:regra_guardar", "Regra do botão “Guardar na pilha”"),
           ("jogo.fase2:regra_aceitar", "Regra do botão “Pôr na custódia”")],
    "f3": [("estruturas.grafo:Grafo.adicionar_aresta", "Grafo por lista de adjacência — aula 09"),
           ("jogo.fase3:mover", "Regras do mapa: vizinho, energia, porta, pista"),
           ("algoritmos.busca_grafo:bfs", "BFS da aula 09 — slides 71–73"),
           ("algoritmos.solver:bfs", "BFS no espaço de estados (o solver da dica)")],
    "f4": [("estruturas.avl:ArvoreAVL._insere", "Inserção na AVL — aula 08"),
           ("estruturas.avl:ArvoreAVL._rotacao_direita", "Rotação direita (RD) — aula 08"),
           ("estruturas.avl:ArvoreAVL._rotacao_esquerda_direita", "Rotação dupla esquerda-direita (RED) — aula 08"),
           ("algoritmos.solver:_Visitados", "A AVL como memória de estados visitados")],
    "f5": [("jogo.fase5:Fase5.etapa_triagem", "Auditoria da Fase 2: refaz cada jogada pelas regras"),
           ("jogo.fase5:Fase5.etapa_mapa", "Auditoria da Fase 3: refaz cada passo pelas regras"),
           ("algoritmos.solver:dfs_recursiva", "DFS recursiva (caso-base e retorno)")],
    "custos": [("estruturas.heap:HeapMinimo._subir", "Heap: subir — aula 08, slide 36"),
               ("algoritmos.dijkstra:relaxa", "Relaxamento — aula 11"),
               ("algoritmos.dijkstra:dijkstra", "Dijkstra — aula 11"),
               ("algoritmos.dijkstra:guloso_ingenuo", "Guloso ingênuo (o que trava)")],
}


def dados_codigo():
    import importlib
    import inspect
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res = {}
    for fase, itens in CODIGO_POR_FASE.items():
        lista = []
        for ref, titulo in itens:
            modulo, nome = ref.split(":")
            obj = importlib.import_module(modulo)
            for parte in nome.split("."):
                obj = getattr(obj, parte)
            linhas, inicio = inspect.getsourcelines(obj)
            arquivo = os.path.relpath(inspect.getsourcefile(obj), raiz).replace(os.sep, "/")
            lista.append({"titulo": titulo, "nome": nome, "arquivo": arquivo, "linha": inicio,
                          "codigo": "".join(linhas).rstrip()})
        res[fase] = lista
    return res


def dados_testes():
    """Roda a suíte de testes e resume por arquivo (só na geração da página, não dentro dos testes)."""
    import io
    import unittest
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suite = unittest.TestLoader().discover(os.path.join(raiz, "testes"), top_level_dir=raiz)
    por = {}

    def contar(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                contar(t)
            else:
                m = t.__class__.__module__.replace("testes.", "")
                por[m] = por.get(m, 0) + 1
    contar(suite)
    r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return {"total": r.testsRun, "falhas": len(r.failures) + len(r.errors), "por_arquivo": sorted(por.items())}


def gerar_dados():
    return {"titulo": narrativa.TITULO, "prologo": narrativa.PROLOGO, "aviso": narrativa.AVISO,
            "capitulos": narrativa.CAPITULOS,
            "fase1": dados_fase1(), "fase2": dados_fase2(), "fase3": dados_fase3(),
            "fase4": dados_fase4(), "fase5": dados_fase5(), "solver": dados_solver(),
            "custos": dados_mapa_custos(), "codigo": dados_codigo(), "motor": dados_motor()}


def dados_motor():
    """"Olhando o código": gravações da execução real, linha a linha (interface/olhando_codigo.py)."""
    from interface.olhando_codigo import dados_motor_fase1, dados_motor_fase3, dados_motor_fase4
    return {"f1": dados_motor_fase1(Fase1().registros, CRITERIOS["auditoria"]), "f3": dados_motor_fase3(),
            "f4": dados_motor_fase4()}


def gerar_html(caminho="jogo.html", com_testes=False):
    """com_testes=True roda a suíte e grava o resultado na tela Resultados (usado ao gerar a página oficial)."""
    modelo = os.path.join(os.path.dirname(__file__), "jogo_web_modelo.html")
    with open(modelo, encoding="utf-8") as arq:
        html = arq.read()
    D = gerar_dados()
    if com_testes:
        D["testes"] = dados_testes()
    html = html.replace("/*__DADOS__*/null", json.dumps(D, ensure_ascii=False, default=str))
    with open(caminho, "w", encoding="utf-8") as arq:
        arq.write(html)
    return os.path.abspath(caminho)


if __name__ == "__main__":
    print(gerar_html(com_testes=True))
