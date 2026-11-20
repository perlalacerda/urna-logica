"""
Gera docs/checklist-entrega.md — a MATRIZ DE INSPEÇÃO para quem avalia o EP.

Para cada conteúdo da disciplina: aula e slides de origem -> função no código
(arquivo:LINHA, calculada agora a partir do código) -> onde aparece no jogo ->
teste que comprova -> seção do relatório técnico.

As linhas não são digitadas à mão: o script importa cada função e pergunta ao
Python onde ela começa (inspect). Se alguém mexer no código, basta rodar de novo:

    py ferramentas/gerar_checklist.py

O script também falha se uma função ou um teste citado deixar de existir,
para a matriz nunca apontar para algo que sumiu.
"""

import importlib
import inspect
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

# (conteúdo, aula e slides, [funções "modulo:Nome.metodo"], onde no jogo, [testes "arquivo:Classe.metodo"], seção do relatório)
LINHAS = [
    ("Vetor de registros e seed", "Aulas 02 e 03 (vetor)", ["jogo.registros:Registro", "jogo.registros:gerar_registros", "jogo.registros:embaralhar"],
     "Fase 1 (as 12 fichas)", ["test_ordenacao:TestRegistros.test_seed_reproduzivel", "test_ordenacao:TestRegistros.test_embaralhar_nao_perde_registros"], "3.1"),
    ("Chave composta (zona, seção, horário)", "Enunciado, Fase 1", ["jogo.registros:chave_composta", "jogo.fase1:Fase1.ordenar"],
     "Fase 1 (montar a regra)", ["test_ordenacao:TestChaveComposta.test_so_pelo_horario_nao_basta", "test_ordenacao:TestChaveMontada.test_so_a_chave_da_regra_e_aceita"], "3.1"),
    ("Bubble Sort iterativo", "Aula 02, slide 10", ["algoritmos.ordenacao:bubble_sort"],
     "Fase 1 e Fase 5", ["test_ordenacao:TestAlgoritmos.test_contadores_bubble"], "6.1"),
    ("Bubble Sort recursivo (caso-base)", "Aula 02, slide 15", ["algoritmos.ordenacao:bubble_sort_recursivo"],
     "Comparação de métodos", ["test_ordenacao:TestAlgoritmos.test_todos_os_casos"], "6.1"),
    ("Merge Sort", "Aula 02, slides 20–22", ["algoritmos.ordenacao:merge_sort"],
     "Fase 1; tabela da Fase 5", ["test_ordenacao:TestChaveComposta.test_tres_algoritmos_concordam", "test_ordenacao:TestAlgoritmos.test_estabilidade"], "6.1"),
    ("Quick Sort (Lomuto)", "Aula 04, slides 31–37", ["algoritmos.ordenacao:quick_sort", "algoritmos.ordenacao:_particiona", "algoritmos.ordenacao:quick_sort_versao_do_slide"],
     "Fase 1 e Fase 5", ["test_ordenacao:TestAlgoritmos.test_quick_versao_literal_do_slide_nao_termina"], "6.1, 10"),
    ("Contagem de operações (análise assintótica)", "Aulas 03 e 04", ["algoritmos.ordenacao:Contador", "experimentos:medir_ordenacao"],
     "Fase 1 (placar e tabela de 500 fichas)", ["test_ordenacao:TestAlgoritmos.test_contadores_bubble"], "8"),
    ("Lista ligada com cabeça", "Aula 06, slides 17–23", ["estruturas.lista_ligada:ListaLigada.inserir_fim", "estruturas.lista_ligada:ListaLigada.remover"],
     "Fase 2 (cofre de custódia); listas de adjacência", ["test_estruturas:TestListaLigada.test_remover_ultimo_atualiza_ponteiro"], "5"),
    ("Pilha (LIFO)", "Aula 06", ["estruturas.pilha:Pilha.push", "estruturas.pilha:Pilha.pop"],
     "Fase 2 (pilha de espera, Desfazer); DFS com pilha", ["test_estruturas:TestPilha.test_pop_vazia_nao_corrompe", "test_fases:TestFase2.test_desfazer_lifo"], "5"),
    ("Fila (FIFO)", "Aula 06", ["estruturas.fila:Fila.enqueue", "estruturas.fila:Fila.dequeue"],
     "Fase 2 (esteira de chegada); BFS", ["test_estruturas:TestFila.test_ordem_fifo"], "5"),
    ("Regras da Fase 2 como funções", "Enunciado, Fase 2", ["jogo.fase2:regra_aceitar", "jogo.fase2:regra_guardar", "jogo.fase2:regra_arquivar", "jogo.fase2:regra_liberar"],
     "Fase 2 (os quatro botões)", ["test_fases:TestRegrasFase2.test_regra_guardar", "test_fases:TestFase2.test_jogada_invalida_nao_altera_estado"], "2"),
    ("Grafo por lista de adjacência", "Aula 09", ["estruturas.grafo:Grafo.adicionar_aresta", "estruturas.grafo:Grafo.vizinhos", "jogo.fase3:construir_mapa"],
     "Fase 3 (o mapa)", ["test_grafo_busca:TestGrafo.test_mapa_do_jogo_atende_o_enunciado"], "3.2"),
    ("BFS da aula (cores, d, π)", "Aula 09, slides 71–73", ["algoritmos.busca_grafo:bfs"],
     "Fase 3 (\"E o caminho mais curto?\")", ["test_grafo_busca:TestBFSDFSdaAula.test_bfs_distancias_da_aula"], "6.2"),
    ("DFS da aula (tempos d e f)", "Aula 09, slides 54–56", ["algoritmos.busca_grafo:dfs"],
     "Comparação no Resolver", ["test_grafo_busca:TestBFSDFSdaAula.test_dfs_tempos"], "6.2"),
    ("Estado e regras do mapa", "Enunciado 7.3–7.5", ["jogo.fase3:regra_adjacencia", "jogo.fase3:regra_energia", "jogo.fase3:regra_porta", "jogo.fase3:mover", "jogo.fase3:chave_estado"],
     "Fase 3 (portas, pistas, energia)", ["test_grafo_busca:TestRegrasFase3.test_mesma_posicao_pistas_diferentes_sao_estados_diferentes"], "3.3"),
    ("Solver: BFS e DFS no espaço de estados", "Aula 09 + enunciado 7", ["algoritmos.solver:bfs", "algoritmos.solver:dfs_recursiva", "algoritmos.solver:dfs_pilha"],
     "Menu Resolver; dicas das Fases 2 e 3", ["test_grafo_busca:TestSolver.test_bfs_nunca_pior_que_dfs_em_numero_de_acoes", "test_grafo_busca:TestSolver.test_solver_resolve_fase2"], "6.3"),
    ("Árvore de busca", "Enunciado 9.2", ["algoritmos.solver:desenhar_arvore_de_busca"],
     "Menu Resolver; visualização", ["test_grafo_busca:TestSolver.test_todas_as_estrategias_respeitam_as_regras"], "6.3"),
    ("Altura de árvore (vazia = −1)", "Aula 07", ["estruturas.avl:altura"],
     "Fase 4 (FB embaixo de cada nó)", ["test_estruturas:TestAVL.test_arvore_vazia"], "5"),
    ("AVL: inserção e rotações RD, RE, RED, RDE", "Aula 08, slides 9–15", ["estruturas.avl:ArvoreAVL._insere", "estruturas.avl:ArvoreAVL._rotacao_direita", "estruturas.avl:ArvoreAVL._rotacao_esquerda",
     "estruturas.avl:ArvoreAVL._rotacao_esquerda_direita", "estruturas.avl:ArvoreAVL._rotacao_direita_esquerda"],
     "Fase 4, Sala 1", ["test_estruturas:TestAVL.test_exemplo_da_aula", "test_fases_finais:TestFase4.test_sala1_quatro_rotacoes_da_aula"], "5"),
    ("AVL como memória de estados visitados", "Aula 08 + enunciado 8", ["algoritmos.solver:_Visitados", "estruturas.avl:ArvoreAVL.buscar"],
     "Fase 4, Salas 2 e 3", ["test_grafo_busca:TestSolver.test_estados_repetidos_nao_sao_expandidos", "test_fases_finais:TestFase4.test_sala2_respostas_calculadas"], "5, 6.3"),
    ("Integração e auditoria final", "Enunciado 9", ["jogo.fase5:Fase5.etapa_lote", "jogo.fase5:Fase5.etapa_triagem", "jogo.fase5:Fase5.etapa_mapa"],
     "Fase 5", ["test_fases_finais:TestFase5.test_integracao_com_o_historico_real_das_fases_2_e_3", "test_fases_finais:TestFase5.test_trilha_invalida_e_recusada"], "2, 7"),
    ("Gerador de mapas por seed (bônus)", "Enunciado 18", ["jogo.cenarios:gerar_mapa"],
     "Métricas (mapa de 30 vértices)", ["test_fases_finais:TestCenarios.test_gerador_reproduzivel_e_com_solucao"], "8"),
    ("Fila de prioridade com heap (bônus)", "Aula 08, slides 23–45", ["estruturas.heap:HeapMinimo.inserir", "estruturas.heap:HeapMinimo._subir",
     "estruturas.heap:HeapMinimo.extrair_minimo", "estruturas.heap:HeapMinimo._descer"],
     "Desafio extra (Mapa com Custos)", ["test_mapa_custos:TestHeap.test_extrai_sempre_o_menor"], "5"),
    ("Dijkstra (guloso que funciona)", "Aula 11", ["algoritmos.dijkstra:inicializa", "algoritmos.dijkstra:relaxa", "algoritmos.dijkstra:dijkstra", "algoritmos.dijkstra:dijkstra_estados"],
     "Desafio extra", ["test_mapa_custos:TestDijkstraDaAula.test_exemplo_da_aula", "test_mapa_custos:TestMapaComCustos.test_dijkstra_e_o_minimo"], "6.4"),
    ("Guloso ingênuo (guloso que falha)", "Aula 11", ["algoritmos.dijkstra:guloso_ingenuo"],
     "Desafio extra (tabela de comparação)", ["test_mapa_custos:TestMapaComCustos.test_guloso_trava"], "6.4"),
]

CAMADAS = [("estruturas", "estruturas de dados (o essencial)"), ("algoritmos", "algoritmos (o essencial)"),
           ("jogo", "regras das fases"), ("interface", "telas (terminal, navegador, visualização)"), ("testes", "testes automáticos")]


def onde(ref):
    """'modulo:Classe.metodo' -> ('arquivo', linha). Falha se não existir."""
    modulo, nome = ref.split(":")
    obj = importlib.import_module(modulo)
    for parte in nome.split("."):
        obj = getattr(obj, parte)
    obj = inspect.unwrap(obj)
    arquivo = os.path.relpath(inspect.getsourcefile(obj), RAIZ).replace(os.sep, "/")
    return arquivo, inspect.getsourcelines(obj)[1]


def onde_teste(ref):
    arquivo, nome = ref.split(":")
    return onde(f"testes.{arquivo}:{nome}")


def link(arquivo, linha, rotulo):
    return f"[`{rotulo}`](../{arquivo}#L{linha})"


def linhas_de_codigo(pasta):
    total = 0
    for nome in sorted(os.listdir(os.path.join(RAIZ, pasta))):
        if nome.endswith(".py"):
            with open(os.path.join(RAIZ, pasta, nome), encoding="utf-8") as f:
                total += sum(1 for _ in f)
    return total


def gerar():
    out = ["# Matriz de inspeção — conteúdo → aula → código → jogo → teste",
           "",
           "> Gerada por `ferramentas/gerar_checklist.py` a partir do código: os números de linha estão sempre atualizados.",
           "> Clique no nome da função para abrir o arquivo na linha exata. Cada função traz, em comentário, o pseudocódigo do slide com a numeração das linhas.",
           "",
           "## Onde está o essencial (curadoria)",
           "",
           "O que a disciplina avalia (estruturas e algoritmos) está em duas pastas. O resto é a camada de jogo e de telas, separada de propósito (seção 12 do enunciado).",
           "",
           "| Pasta | O que tem | Linhas |",
           "|---|---|---|"]
    for pasta, desc in CAMADAS:
        out.append(f"| `{pasta}/` | {desc} | {linhas_de_codigo(pasta)} |")
    out += ["", "## Matriz", "",
            "| # | Conteúdo | Aula e slides | Código (arquivo:linha) | Onde no jogo | Teste que comprova | Relatório § |",
            "|---|---|---|---|---|---|---|"]
    for i, (conteudo, aula, funcs, jogo, testes, sec) in enumerate(LINHAS, 1):
        codigo = "<br>".join(link(*onde(f), f"{f.split(':')[1]} — {onde(f)[0]}:{onde(f)[1]}") for f in funcs)
        tst = "<br>".join(link(*onde_teste(t), t.split(":")[1].split(".")[-1]) for t in testes)
        out.append(f"| {i} | {conteudo} | {aula} | {codigo} | {jogo} | {tst} | {sec} |")
    out += ["", "## Como conferir em 3 minutos", "",
            "1. Rodar os testes: `rodar_testes.bat` (Windows) ou `python -m unittest discover -s testes -t .` — deve terminar em `OK`.",
            "2. Abrir um algoritmo pela matriz e comparar o comentário com o slide citado.",
            "3. Jogar a fase correspondente (coluna \"Onde no jogo\") e ver o mesmo algoritmo em ação.",
            ""]
    destino = os.path.join(RAIZ, "docs", "checklist-entrega.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return destino, len(LINHAS)


if __name__ == "__main__":
    caminho, n = gerar()
    print(f"{n} linhas gravadas em {os.path.relpath(caminho, RAIZ)}")
