# Matriz de inspeção — conteúdo → aula → código → jogo → teste

> Gerada por `ferramentas/gerar_checklist.py` a partir do código: os números de linha estão sempre atualizados.
> Clique no nome da função para abrir o arquivo na linha exata. Cada função traz, em comentário, o pseudocódigo do slide com a numeração das linhas.

## Onde está o essencial (curadoria)

O que a disciplina avalia (estruturas e algoritmos) está em duas pastas. O resto é a camada de jogo e de telas, separada de propósito (seção 12 do enunciado).

| Pasta | O que tem | Linhas |
|---|---|---|
| `estruturas/` | estruturas de dados (o essencial) | 915 |
| `algoritmos/` | algoritmos (o essencial) | 957 |
| `jogo/` | regras das fases | 1531 |
| `interface/` | telas (terminal, navegador, visualização) | 1455 |
| `testes/` | testes automáticos | 1533 |

## Matriz

| # | Conteúdo | Aula e slides | Código (arquivo:linha) | Onde no jogo | Teste que comprova | Relatório § |
|---|---|---|---|---|---|---|
| 1 | Vetor de registros e seed | Aulas 02 e 03 (vetor) | [`Registro — jogo/registros.py:26`](../jogo/registros.py#L26)<br>[`gerar_registros — jogo/registros.py:93`](../jogo/registros.py#L93)<br>[`embaralhar — jogo/registros.py:114`](../jogo/registros.py#L114) | Fase 1 (as 12 fichas) | [`test_seed_reproduzivel`](../testes/test_ordenacao.py#L133)<br>[`test_embaralhar_nao_perde_registros`](../testes/test_ordenacao.py#L140) | 3.1 |
| 2 | Chave composta (zona, seção, horário) | Enunciado, Fase 1 | [`chave_composta — jogo/registros.py:76`](../jogo/registros.py#L76)<br>[`Fase1.ordenar — jogo/fase1.py:50`](../jogo/fase1.py#L50) | Fase 1 (montar a regra) | [`test_so_pelo_horario_nao_basta`](../testes/test_ordenacao.py#L125)<br>[`test_so_a_chave_da_regra_e_aceita`](../testes/test_ordenacao.py#L176) | 3.1 |
| 3 | Bubble Sort iterativo | Aula 02, slide 10 | [`bubble_sort — algoritmos/ordenacao.py:51`](../algoritmos/ordenacao.py#L51) | Fase 1 e Fase 5 | [`test_contadores_bubble`](../testes/test_ordenacao.py#L44) | 6.1 |
| 4 | Bubble Sort recursivo (caso-base) | Aula 02, slide 15 | [`bubble_sort_recursivo — algoritmos/ordenacao.py:80`](../algoritmos/ordenacao.py#L80) | Comparação de métodos | [`test_todos_os_casos`](../testes/test_ordenacao.py#L35) | 6.1 |
| 5 | Merge Sort | Aula 02, slides 20–22 | [`merge_sort — algoritmos/ordenacao.py:108`](../algoritmos/ordenacao.py#L108) | Fase 1; tabela da Fase 5 | [`test_tres_algoritmos_concordam`](../testes/test_ordenacao.py#L118)<br>[`test_estabilidade`](../testes/test_ordenacao.py#L58) | 6.1 |
| 6 | Quick Sort (Lomuto) | Aula 04, slides 31–37 | [`quick_sort — algoritmos/ordenacao.py:165`](../algoritmos/ordenacao.py#L165)<br>[`_particiona — algoritmos/ordenacao.py:197`](../algoritmos/ordenacao.py#L197)<br>[`quick_sort_versao_do_slide — algoritmos/ordenacao.py:223`](../algoritmos/ordenacao.py#L223) | Fase 1 e Fase 5 | [`test_quick_versao_literal_do_slide_nao_termina`](../testes/test_ordenacao.py#L50) | 6.1, 10 |
| 7 | Contagem de operações (análise assintótica) | Aulas 03 e 04 | [`Contador — algoritmos/ordenacao.py:38`](../algoritmos/ordenacao.py#L38)<br>[`medir_ordenacao — experimentos.py:33`](../experimentos.py#L33) | Fase 1 (placar e tabela de 500 fichas) | [`test_contadores_bubble`](../testes/test_ordenacao.py#L44) | 8 |
| 8 | Lista ligada com cabeça | Aula 06, slides 17–23 | [`ListaLigada.inserir_fim — estruturas/lista_ligada.py:96`](../estruturas/lista_ligada.py#L96)<br>[`ListaLigada.remover — estruturas/lista_ligada.py:123`](../estruturas/lista_ligada.py#L123) | Fase 2 (cofre de custódia); listas de adjacência | [`test_remover_ultimo_atualiza_ponteiro`](../testes/test_estruturas.py#L123) | 5 |
| 9 | Pilha (LIFO) | Aula 06 | [`Pilha.push — estruturas/pilha.py:32`](../estruturas/pilha.py#L32)<br>[`Pilha.pop — estruturas/pilha.py:44`](../estruturas/pilha.py#L44) | Fase 2 (pilha de espera, Desfazer); DFS com pilha | [`test_pop_vazia_nao_corrompe`](../testes/test_estruturas.py#L44)<br>[`test_desfazer_lifo`](../testes/test_fases.py#L114) | 5 |
| 10 | Fila (FIFO) | Aula 06 | [`Fila.enqueue — estruturas/fila.py:33`](../estruturas/fila.py#L33)<br>[`Fila.dequeue — estruturas/fila.py:55`](../estruturas/fila.py#L55) | Fase 2 (fila de chegada); BFS | [`test_ordem_fifo`](../testes/test_estruturas.py#L69) | 5 |
| 11 | Regras da Fase 2 como funções | Enunciado, Fase 2 | [`regra_aceitar — jogo/fase2.py:62`](../jogo/fase2.py#L62)<br>[`regra_guardar — jogo/fase2.py:72`](../jogo/fase2.py#L72)<br>[`regra_arquivar — jogo/fase2.py:83`](../jogo/fase2.py#L83)<br>[`regra_liberar — jogo/fase2.py:90`](../jogo/fase2.py#L90) | Fase 2 (os quatro botões) | [`test_regra_guardar`](../testes/test_fases.py#L74)<br>[`test_jogada_invalida_nao_altera_estado`](../testes/test_fases.py#L103) | 2 |
| 12 | Grafo por lista de adjacência | Aula 09 | [`Grafo.adicionar_aresta — estruturas/grafo.py:43`](../estruturas/grafo.py#L43)<br>[`Grafo.vizinhos — estruturas/grafo.py:75`](../estruturas/grafo.py#L75)<br>[`construir_mapa — jogo/fase3.py:68`](../jogo/fase3.py#L68) | Fase 3 (o mapa) | [`test_mapa_do_jogo_atende_o_enunciado`](../testes/test_grafo_busca.py#L56) | 3.2 |
| 13 | BFS da aula (cores, d, π) | Aula 09, slides 71–73 | [`bfs — algoritmos/busca_grafo.py:22`](../algoritmos/busca_grafo.py#L22) | Fase 3 ("E o caminho mais curto?") | [`test_bfs_distancias_da_aula`](../testes/test_grafo_busca.py#L65) | 6.2 |
| 14 | DFS da aula (tempos d e f) | Aula 09, slides 54–56 | [`dfs — algoritmos/busca_grafo.py:61`](../algoritmos/busca_grafo.py#L61) | Comparação no Resolver | [`test_dfs_tempos`](../testes/test_grafo_busca.py#L102) | 6.2 |
| 15 | Estado e regras do mapa | Enunciado 7.3–7.5 | [`regra_adjacencia — jogo/fase3.py:78`](../jogo/fase3.py#L78)<br>[`regra_energia — jogo/fase3.py:84`](../jogo/fase3.py#L84)<br>[`regra_porta — jogo/fase3.py:93`](../jogo/fase3.py#L93)<br>[`mover — jogo/fase3.py:106`](../jogo/fase3.py#L106)<br>[`chave_estado — jogo/fase3.py:134`](../jogo/fase3.py#L134) | Fase 3 (portas, pistas, energia) | [`test_mesma_posicao_pistas_diferentes_sao_estados_diferentes`](../testes/test_grafo_busca.py#L115) | 3.3 |
| 16 | Solver: BFS e DFS no espaço de estados | Aula 09 + enunciado 7 | [`bfs — algoritmos/solver.py:146`](../algoritmos/solver.py#L146)<br>[`dfs_recursiva — algoritmos/solver.py:186`](../algoritmos/solver.py#L186)<br>[`dfs_pilha — algoritmos/solver.py:234`](../algoritmos/solver.py#L234) | Menu Resolver; dicas das Fases 2 e 3 | [`test_bfs_nunca_pior_que_dfs_em_numero_de_acoes`](../testes/test_grafo_busca.py#L183)<br>[`test_solver_resolve_fase2`](../testes/test_grafo_busca.py#L219) | 6.3 |
| 17 | Árvore de busca | Enunciado 9.2 | [`desenhar_arvore_de_busca — algoritmos/solver.py:281`](../algoritmos/solver.py#L281) | Menu Resolver; visualização | [`test_todas_as_estrategias_respeitam_as_regras`](../testes/test_grafo_busca.py#L168) | 6.3 |
| 18 | Altura de árvore (vazia = −1) | Aula 07 | [`altura — estruturas/avl.py:38`](../estruturas/avl.py#L38) | Fase 4 (FB embaixo de cada nó) | [`test_arvore_vazia`](../testes/test_estruturas.py#L207) | 5 |
| 19 | AVL: inserção e rotações RD, RE, RED, RDE | Aula 08, slides 16–21 (algoritmo) e 9–15 (exemplo) | [`ArvoreAVL._insere — estruturas/avl.py:141`](../estruturas/avl.py#L141)<br>[`ArvoreAVL._rotacao_direita — estruturas/avl.py:57`](../estruturas/avl.py#L57)<br>[`ArvoreAVL._rotacao_esquerda — estruturas/avl.py:79`](../estruturas/avl.py#L79)<br>[`ArvoreAVL._rotacao_esquerda_direita — estruturas/avl.py:101`](../estruturas/avl.py#L101)<br>[`ArvoreAVL._rotacao_direita_esquerda — estruturas/avl.py:113`](../estruturas/avl.py#L113) | Fase 4, Sala 1 | [`test_exemplo_da_aula`](../testes/test_estruturas.py#L150)<br>[`test_sala1_quatro_rotacoes_da_aula`](../testes/test_fases_finais.py#L21) | 5 |
| 20 | AVL como memória de estados visitados | Aula 08 + enunciado 8 | [`_Visitados — algoritmos/solver.py:80`](../algoritmos/solver.py#L80)<br>[`ArvoreAVL.buscar — estruturas/avl.py:178`](../estruturas/avl.py#L178) | Fase 4, Salas 2 e 3 | [`test_estados_repetidos_nao_sao_expandidos`](../testes/test_grafo_busca.py#L197)<br>[`test_sala2_respostas_calculadas`](../testes/test_fases_finais.py#L48) | 5, 6.3 |
| 21 | Integração e auditoria final | Enunciado 9 | [`Fase5.etapa_lote — jogo/fase5.py:50`](../jogo/fase5.py#L50)<br>[`Fase5.etapa_triagem — jogo/fase5.py:71`](../jogo/fase5.py#L71)<br>[`Fase5.etapa_mapa — jogo/fase5.py:91`](../jogo/fase5.py#L91) | Fase 5 | [`test_integracao_com_o_historico_real_das_fases_2_e_3`](../testes/test_fases_finais.py#L93)<br>[`test_trilha_invalida_e_recusada`](../testes/test_fases_finais.py#L116) | 2, 7 |
| 22 | Gerador de mapas por seed (bônus) | Enunciado 18 | [`gerar_mapa — jogo/cenarios.py:26`](../jogo/cenarios.py#L26) | Métricas (mapa de 30 vértices) | [`test_gerador_reproduzivel_e_com_solucao`](../testes/test_fases_finais.py#L133) | 8 |
| 23 | Fila de prioridade com heap (bônus) | Aula 08, slides 23–45 | [`HeapMinimo.inserir — estruturas/heap.py:66`](../estruturas/heap.py#L66)<br>[`HeapMinimo._subir — estruturas/heap.py:83`](../estruturas/heap.py#L83)<br>[`HeapMinimo.extrair_minimo — estruturas/heap.py:100`](../estruturas/heap.py#L100)<br>[`HeapMinimo._descer — estruturas/heap.py:122`](../estruturas/heap.py#L122) | Desafio extra (Mapa com Custos) | [`test_extrai_sempre_o_menor`](../testes/test_mapa_custos.py#L28) | 5 |
| 24 | Dijkstra (guloso que funciona) | Aula 11 | [`inicializa — algoritmos/dijkstra.py:54`](../algoritmos/dijkstra.py#L54)<br>[`relaxa — algoritmos/dijkstra.py:71`](../algoritmos/dijkstra.py#L71)<br>[`dijkstra — algoritmos/dijkstra.py:87`](../algoritmos/dijkstra.py#L87)<br>[`dijkstra_estados — algoritmos/dijkstra.py:126`](../algoritmos/dijkstra.py#L126) | Desafio extra | [`test_exemplo_da_aula`](../testes/test_mapa_custos.py#L76)<br>[`test_dijkstra_e_o_minimo`](../testes/test_mapa_custos.py#L114) | 6.4 |
| 25 | Guloso ingênuo (guloso que falha) | Aula 11 | [`guloso_ingenuo — algoritmos/dijkstra.py:204`](../algoritmos/dijkstra.py#L204) | Desafio extra (tabela de comparação) | [`test_guloso_trava`](../testes/test_mapa_custos.py#L130) | 6.4 |

## Como conferir em 3 minutos

1. Rodar os testes: `rodar_testes.bat` (Windows) ou `python -m unittest discover -s testes -t .` — deve terminar em `OK`.
2. Abrir um algoritmo pela matriz e comparar o comentário com o slide citado.
3. Jogar a fase correspondente (coluna "Onde no jogo") e ver o mesmo algoritmo em ação.
