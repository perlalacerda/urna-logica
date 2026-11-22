"""
FASE 5 — A Auditoria Final                           (seção 9 do enunciado)

Integra as fases anteriores. Cada etapa é ENCONTRADA ou VALIDADA pelo solver,
nunca aceita "porque sim":

  Etapa 1 — Lote     : gera o lote (seed), ordena com o algoritmo escolhido e
                       confere: ordem da auditoria, nenhum registro perdido,
                       nenhum id duplicado.
  Etapa 2 — Triagem  : se o jogador já resolveu a Fase 2, suas ações são
                       REEXECUTADAS com as regras (validação). Senão, a BFS
                       encontra uma solução.
  Etapa 3 — Mapa     : idem com a trilha da Fase 3, conferida movimento a
                       movimento pela função mover() (mesmas regras R1-R5).
  Etapa 4 — Relatório: junta tudo, compara BFS x DFS em dois cenários e
                       ORDENA os resultados com Merge Sort (item 9.3).

A trilha é CONSISTENTE quando as três etapas passam. Isso dá o Selo 5;
com os 5 selos, o Cofre de Verificação se abre (fim do jogo).
"""

import os
import platform
import sys

from algoritmos.ordenacao import merge_sort, primeiro_fora_de_ordem
from algoritmos.solver import bfs, dfs_recursiva, dfs_pilha
from jogo.fase1 import Fase1, CHAVE_AUDITORIA
from jogo.fase2 import Fase2, ProblemaTriagem
from jogo.fase3 import (ProblemaMapa, construir_mapa, mover, estado_inicial,
                        DESTINO, rotulo)
from jogo.cenarios import cenarios_de_comparacao
from jogo.registros import gerar_registros, validar_ids_unicos


class Fase5:
    NOME = "Fase 5 — A Auditoria Final"
    ABERTURA = ("Todos os selos foram recuperados (ou quase!).\n"
                "Agora é preciso reconstruir a trilha completa, conferir as evidências e\n"
                "demonstrar que o resultado decorre das regras, e não de uma resposta pré-programada.")

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.etapas = {}          # nome -> dicionário com o resultado
        self.comparacao = None

    # ---------------------------------------------------- etapa 1
    def etapa_lote(self, seed=2042, n=12, algoritmo="merge"):
        f = Fase1(seed=seed, n=n)
        ids_antes = sorted(r.id_registro for r in f.registros)
        res = f.ordenar(algoritmo, "auditoria")
        ids_depois = sorted(r.id_registro for r in f.registros)
        checagens = [
            ("lote ordenado por zona, seção, horário",
             primeiro_fora_de_ordem(f.registros, CHAVE_AUDITORIA) == -1),
            ("nenhum registro perdido ou criado", ids_antes == ids_depois),
            ("nenhum identificador duplicado", validar_ids_unicos(f.registros) == []),
        ]
        c = res["contador"]
        self.etapas["lote"] = {
            "ok": all(ok for _, ok in checagens), "checagens": checagens,
            "detalhe": f"seed {seed}, {n} registros, {c.algoritmo}: "
                       f"{c.comparacoes} comparações, {c.movimentacoes} movimentações",
            "registros": f.registros,
        }
        return self.etapas["lote"]

    # ---------------------------------------------------- etapa 2
    def etapa_triagem(self, acoes_do_jogador=None):
        # aceita tanto ["guardar", ...] quanto o histórico da Fase 2: [("guardar", "E1"), ...]
        if acoes_do_jogador:
            acoes_do_jogador = [a[0] if isinstance(a, tuple) else a for a in acoes_do_jogador]
            f = Fase2()
            passos_ok = all(f.executar(a)[0] for a in acoes_do_jogador)
            ok, origem, acoes = passos_ok and f.venceu(), "jogador (validado pelas regras do jogo, as mesmas do solver)", list(acoes_do_jogador)
            metricas = "ações do jogador reexecutadas uma a uma com as regras R1-R5"
        else:
            r = bfs(ProblemaTriagem())
            ok, origem, acoes = r.encontrou, "solver (BFS)", [a for a, _ in r.caminho[1:]]
            metricas = (f"{r.expandidos} estados expandidos, {r.repetidos} repetidos ignorados, "
                        f"{r.tempo_ms:.3f} ms")
        self.etapas["triagem"] = {
            "ok": ok, "origem": origem, "detalhe": " -> ".join(acoes), "metricas": metricas,
            "checagens": [("custódia E2 -> E4 -> E1 -> E6, fila e pilha vazias", ok)],
        }
        return self.etapas["triagem"]

    # ---------------------------------------------------- etapa 3
    def etapa_mapa(self, trilha_do_jogador=None):
        G = construir_mapa()
        if trilha_do_jogador and len(trilha_do_jogador) > 1:
            e, valido = estado_inicial(), True
            for v in trilha_do_jogador[1:]:
                valido, e, _ = mover(G, e, v)
                if not valido:
                    break
            ok = valido and e[0] == DESTINO
            origem, trilha, final = "jogador (validado pelas regras do jogo, as mesmas do solver)", list(trilha_do_jogador), e
            metricas = "cada movimento conferido pela função mover() (regras R1-R5)"
        else:
            r = bfs(ProblemaMapa(G))
            ok, origem = r.encontrou, "solver (BFS)"
            trilha = [e[0] for _, e in r.caminho]
            final = r.caminho[-1][1] if r.encontrou else None
            metricas = (f"{r.expandidos} estados expandidos, {r.repetidos} repetidos ignorados, "
                        f"custo {r.custo}, {r.tempo_ms:.3f} ms")
        self.etapas["mapa"] = {
            "ok": ok, "origem": origem, "detalhe": " -> ".join(trilha), "metricas": metricas,
            "final": rotulo(final) if final else "-",
            "checagens": [("chegou ao Centro de Validação com AUT, sem violar portas", ok)],
        }
        return self.etapas["mapa"]

    # ---------------------------------------------------- etapa 4
    def comparar_estrategias(self, seed=2042):
        """BFS x DFS em dois cenários; resultados ORDENADOS com Merge Sort (item 9.3)."""
        linhas = []
        for nome, problema in cenarios_de_comparacao(seed):
            for alg in (bfs, dfs_recursiva, dfs_pilha):
                r = alg(problema)
                linhas.append({"cenario": nome, "estrategia": r.algoritmo,
                               "acoes": r.numero_acoes() if r.encontrou else None,
                               "expandidos": r.expandidos, "gerados": r.gerados,
                               "repetidos": r.repetidos, "fronteira": r.maior_fronteira,
                               "avl_altura": r.avl_altura, "avl_rotacoes": r.avl_rotacoes,
                               "tempo_ms": r.tempo_ms})
        # ordenação do relatório: por cenário e, dentro dele, por estados expandidos
        merge_sort(linhas, lambda x: (x["cenario"], x["expandidos"], x["estrategia"]))
        self.comparacao = linhas
        return linhas

    def consistente(self):
        return all(self.etapas.get(k, {}).get("ok") for k in ("lote", "triagem", "mapa"))

    def venceu(self):
        return self.consistente()

    def relatorio_texto(self):
        """Relatório de encerramento (texto), também gravado em arquivo."""
        L = ["RELATÓRIO DE CONSISTÊNCIA — AUDITORIA DE VERÍDIA (dados fictícios)", "=" * 68]
        nomes = {"lote": "Etapa 1 — Lote de registros", "triagem": "Etapa 2 — Central de Triagem",
                 "mapa": "Etapa 3 — Mapa das Seções"}
        for chave, titulo in nomes.items():
            e = self.etapas.get(chave)
            L.append(f"\n{titulo}: {'CONSISTENTE' if e and e['ok'] else 'NÃO CONSISTENTE' if e else 'não executada'}")
            if not e:
                continue
            if "origem" in e:
                L.append(f"  Origem da solução: {e['origem']}")
            L.append(f"  {e['detalhe']}")
            if "metricas" in e:
                L.append(f"  Métricas: {e['metricas']}")
            if "final" in e:
                L.append(f"  Estado final: {e['final']}")
            for desc, ok in e["checagens"]:
                L.append(f"  [{'ok' if ok else 'FALHOU'}] {desc}")
        if self.comparacao:
            L.append("\nComparação BFS x DFS (ordenada por cenário e estados expandidos, com Merge Sort)")
            L.append(f"  {'estratégia':17} {'ações':>5} {'expand.':>7} {'gerados':>7} {'repet.':>6} "
                     f"{'front.':>6} {'AVL h':>5} {'rot.':>4} {'ms':>8}")
            atual = None
            for x in self.comparacao:
                if x["cenario"] != atual:
                    atual = x["cenario"]
                    L.append(f"  {atual}")
                L.append(f"  {x['estrategia']:17} {x['acoes'] if x['acoes'] is not None else '-':>5} "
                         f"{x['expandidos']:>7} {x['gerados']:>7} {x['repetidos']:>6} {x['fronteira']:>6} "
                         f"{x['avl_altura']:>5} {x['avl_rotacoes']:>4} {x['tempo_ms']:>8.3f}")
        L.append(f"\nConclusão: a trilha {'É' if self.consistente() else 'NÃO é'} consistente segundo as regras fictícias.")
        L.append(f"Ambiente: Python {sys.version.split()[0]}, {platform.system()} {platform.release()}.")
        return "\n".join(L)

    def gravar_relatorio(self, pasta="resultados"):
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, "relatorio_auditoria.txt")
        with open(caminho, "w", encoding="utf-8") as arq:
            arq.write(self.relatorio_texto() + "\n")
        return caminho
