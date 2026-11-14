# Guia código × conceitos — Urna Lógica

Este guia liga cada conceito da disciplina ao lugar exato onde ele aparece no jogo e no código. Serve para estudar, apresentar e responder perguntas.

Todo o conteúdo é elaboração da equipe (com apoio de IAG, registrado em `docs/registro-iag.md`), a partir do enunciado do EP e das aulas da Profa. Lucy Mari Tabuti. Os números citados vêm de `docs/metricas.md` (gerado por `experimentos.py`) e dos testes em `testes/`.

**Como usar cada cartão**

| Campo | Pergunta que responde |
|---|---|
| No jogo | Onde o jogador "sente" o conceito? |
| No código | Qual arquivo e qual função abrir? |
| A ideia | O que o algoritmo faz, em palavras simples |
| Complexidade | Quanto custa, e por quê |
| Prova | Qual teste demonstra que funciona |
| Para mostrar | Caminho no menu ou na visualização |

---

## Parte 0 — Python para quem programou em COBOL

O código foi escrito para ler quase como pseudocódigo. Este quadro traduz o essencial.

| COBOL | Python | Observação |
|---|---|---|
| `PERFORM VARYING I FROM 0 BY 1 UNTIL I > J - 1` | `for i in range(0, j):` | `range(0, j)` gera 0, 1, …, j−1 |
| `PERFORM UNTIL fim` | `while not fim:` | |
| `IF … ELSE … END-IF` | `if …:` / `else:` | O bloco é marcado pela **indentação**, não por `END-IF` |
| Parágrafo / SECTION | `def nome(parâmetros):` | `return` devolve o resultado |
| Registro nível 01 | `class` | A classe junta dados (campos) e rotinas (métodos) |
| Campo do registro | `self.campo` | `self` = "este objeto" |
| Tabela `OCCURS` | lista `[a, b, c]` | Cresce sozinha; índice começa em 0 |
| Valor nulo | `None` | Faz o papel do `NULL` dos slides |
| Grupo de campos fixo | tupla `(zona, secao, hora)` | Compara campo a campo, como uma chave composta |
| Arquivo indexado por chave | `dict` (dicionário) | Usado só como apoio; as estruturas avaliadas são próprias |
| `MOVE A TO B` e troca com auxiliar | `A[i], A[j] = A[j], A[i]` | Troca dois valores numa linha |

Convenção do projeto: **cada função traz em comentário o pseudocódigo do slide**, com os números de linha (`# 1`, `# 2`…). Dá para abrir o slide ao lado e seguir linha a linha.

---

## Parte 1 — Visão geral

```
jogo.py ──► interface/terminal.py ──► jogo/fase1..fase5.py ──► algoritmos/ ──► estruturas/
 (início)      (telas, sem regras)       (regras do jogo)        (ordenação,      (lista, pilha,
                                                                  BFS/DFS,         fila, AVL,
                                                                  solver)          grafo)
```

**Ideia central do projeto:** cada fase descreve um *problema de busca*: um estado inicial, as ações válidas a partir de cada estado e um teste de objetivo. O jogador escolhe as ações; o solver (BFS ou DFS) as explora sozinho. Os dois usam **as mesmas funções de regra**. Por isso o solver não traz resposta pronta: ele encontra a solução a partir das regras (Etapa 11 do EP).

| Fase | Conceitos | Arquivo |
|---|---|---|
| 1 — Arquivo Embaralhado | vetor, registro, seed, Bubble/Merge/Quick, chave composta | `jogo/fase1.py`, `jogo/registros.py`, `algoritmos/ordenacao.py` |
| 2 — Central de Triagem | fila, pilha, lista ligada, desfazer, espaço de estados | `jogo/fase2.py`, `estruturas/` |
| 3 — Mapa das Seções | grafo, lista de adjacência, BFS, DFS, estado | `jogo/fase3.py`, `estruturas/grafo.py`, `algoritmos/busca_grafo.py`, `algoritmos/solver.py` |
| 4 — Cofre dos Estados | AVL, rotações, chave de estado | `jogo/fase4.py`, `estruturas/avl.py` |
| 5 — Auditoria Final | integração, solver, métricas, ordenação do relatório | `jogo/fase5.py`, `jogo/cenarios.py` |

---

## Parte 2 — Cartões dos conceitos obrigatórios (seção 10 do EP)

### 1. Vetor e registro

- **No jogo:** Fase 1 — o lote de 12 registros fictícios exibido em tabela.
- **No código:** `jogo/registros.py` → classe `Registro` (campos `id_registro`, `zona`, `secao`, `opcao`, `timestamp`, `status`). Os registros ficam numa lista Python, acesso por índice `A[i]`.
- **A ideia:** o registro agrupa os campos de um voto fictício; o vetor guarda os registros em sequência. Zona, seção e horário são textos de tamanho fixo (`"03"`, `"014"`, `"18:42:10"`); com isso, a ordem alfabética coincide com a ordem numérica e cronológica.
- **Complexidade:** acesso a `A[i]` em O(1).
- **Prova:** `testes/test_ordenacao.py` → `TestRegistros` (vetor vazio, um registro, ids repetidos detectados, carga de 300 registros).
- **Para mostrar:** Jogar → Fase 1.

### 2. Aleatoriedade e seed

- **No jogo:** o lote chega embaralhado, mas sempre igual (seed 2042).
- **No código:** `jogo/registros.py` → `gerar_registros(n, seed)` e `embaralhar(A, seed)`.
- **A ideia:** `random.Random(seed)` produz sempre a mesma sequência de "sorteios" para a mesma seed. O embaralhamento é o **Fisher–Yates**, implementado pela equipe: para i de n−1 até 1, sorteia j entre 0 e i e troca A[i] com A[j]. Cada uma das n! ordens tem a mesma chance.
- **Complexidade:** O(n).
- **Prova:** `test_seed_reproduzivel` (mesma seed → mesmo lote; seed diferente → lote diferente) e `test_embaralhar_nao_perde_registros`.
- **Detalhe de projeto:** o gerador sorteia poucos horários (cerca de n/3) para *garantir* horários repetidos em zonas diferentes, condição do enigma 5.3 (`test_lote_tem_horarios_repetidos_em_zonas_diferentes`).

### 3. Bubble Sort (aula 02, slides 10–15)

- **No jogo:** Fase 1, opção "Ordenar" → 1.
- **No código:** `algoritmos/ordenacao.py` → `bubble_sort` (iterativo) e `bubble_sort_recursivo`.
- **A ideia:** compara vizinhos e troca os que estão fora de ordem. A cada passada j, o maior elemento ainda solto "borbulha" até a posição j.
- **Complexidade:** comparações = (n−1) + (n−2) + … + 1 = **n(n−1)/2 = Θ(n²)**, em qualquer entrada. Medido: n = 1.000 → 499.500 comparações (aleatório, ordenado ou invertido).
- **Prova:** `test_contadores_bubble` (vetor [5,4,3,2,1]: 10 comparações = 5·4/2) e `test_todos_os_casos`.
- **Para mostrar:** visualização → aba Ordenação → Bubble Sort.

### 4. Merge Sort (aula 02, slides 20–22; aula 04)

- **No código:** `merge_sort` com a função interna `merge`, iguais ao slide 21, inclusive a cópia da metade direita **invertida** no vetor auxiliar B.
- **A ideia:** divisão e conquista — divide ao meio, ordena cada metade (recursão), intercala as duas metades ordenadas.
- **Complexidade:** T(n) = 2T(n/2) + Θ(n) = **Θ(n log n)** em todos os casos (aula 04). Medido: n = 1.000 → 9.976 comparações.
- **Ponto de atenção:** essa versão **não é estável** (pode inverter registros de chave igual). Ver cartão 6.
- **Prova:** `test_todos_os_casos` usa o exemplo do slide 22 (`[12, 35, 87, 26, 9, 28, 7]`).

### 5. Quick Sort (aula 04, slides 31–37)

- **No código:** `quick_sort` e `_particiona` (pivô = último elemento, como no slide 32).
- **A ideia:** escolhe um pivô, coloca os menores à esquerda e os maiores à direita (particiona) e ordena cada lado recursivamente.
- **Complexidade:** caso médio **Θ(n log n)**; pior caso **Θ(n²)** quando a entrada já está ordenada ou invertida. Medido: n = 1.000 já ordenado → **499.500 comparações = n(n−1)/2**, exatamente a recorrência T(n) = T(n−1) + Θ(n) do slide 35.
- **Achado da equipe (bom para a apresentação):** o slide 31 chama `quickSort(A, p, q)`. Com esse particiona, se o pivô for o maior valor, q = r e a mesma chamada se repete para sempre. Usamos `p..q−1` (Cormen). A função `quick_sort_versao_do_slide` reproduz o slide literalmente, e o teste `test_quick_versao_literal_do_slide_nao_termina` mostra o laço infinito (em Python, `RecursionError`). **Pendente de confirmação com a professora.**

### 6. Chave composta e estabilidade

- **No jogo:** enigma da Fase 1 — ordenar por zona, depois seção, depois horário.
- **No código:** `jogo/registros.py` → `CRITERIOS["auditoria"] = (zona, secao, timestamp, id_registro)`.
- **A ideia:** a tupla é comparada campo a campo, como num dicionário: só olha o 2.º campo se o 1.º empatar. Ordenar só pelo horário viola a regra (`test_so_pelo_horario_nao_basta`).
- **Por que o `id_registro` no fim:** Merge (versão da aula) e Quick não são estáveis — em 200 vetores de teste com chaves repetidas, o Merge trocou a ordem de iguais em 96 e o Quick em 178; o Bubble, em nenhum (`test_estabilidade`). Sem desempate, registros com zona, seção e horário iguais poderiam sair em ordens diferentes em cada algoritmo, e o teste "os três algoritmos dão o mesmo resultado" falharia. O id é único: a ordem final passa a ser uma só (`test_tres_algoritmos_concordam`).
- **Para mostrar:** no lote padrão, VR-0006 e VR-0012 empatam em zona 03, seção 001, 18:42:10 — o id desempata.

### 7. Recursão

| Onde | Caso-base | Chamada recursiva | Retorno |
|---|---|---|---|
| `bubble_sort_recursivo` | n ≤ 1 | `bubble(n − 1)` | nada (ordena no lugar) |
| `merge_sort` → `ordena` | p ≥ r (0 ou 1 elemento) | `ordena(p, q)` e `ordena(q+1, r)` | nada |
| `quick_sort` → `ordena` | p ≥ r | `ordena(p, q−1)` e `ordena(q+1, r)` | nada |
| `busca_grafo.dfs` → `visita_dfs` | nenhum vizinho BRANCO | `visita_dfs(v)` | marca PRETO e o tempo f[u] |
| `solver.dfs_recursiva` → `visita` | (1) estado é objetivo; (2) nenhum sucessor leva ao objetivo | `visita(v)` | devolve o objetivo, ou `None` (beco sem saída) |
| `ArvoreAVL._insere` | árvore vazia (`r is None`) | `_insere(r.esq, …)` ou `_insere(r.dir, …)` | a raiz da subárvore, já balanceada |

- **Recursão × pilha:** a aula 06 mostra que todo algoritmo recursivo pode virar iterativo com uma pilha explícita. O projeto traz os dois lados: `dfs_recursiva` (pilha de chamadas do Python) e `dfs_pilha` (nossa `Pilha`).
- **Limite prático:** o Python limita a profundidade da recursão; `_garantir_pilha_de_recursao` aumenta esse limite para o Quick Sort no pior caso. Limitação registrada no relatório.

### 8. Pilha — LIFO (aula 06, slides 24–32)

- **No jogo:** Fase 2 — pilha de espera e **desfazer**; Fase 3 — desfazer movimento; solver — DFS iterativa.
- **No código:** `estruturas/pilha.py` → `push`, `pop`, `peek`, `esta_vazia` (implementação dinâmica, igual aos slides 30–31).
- **A ideia:** o último a entrar é o primeiro a sair. O desfazer guarda, a cada ação válida, uma "foto" do estado; desfazer restaura a foto mais recente.
- **Decisão:** `pop` em pilha vazia devolve `(False, None)`, como o `retorna false` do slide, em vez de quebrar o programa (seção 6.4 do EP).
- **Complexidade:** O(1) em todas as operações.
- **Prova:** `TestPilha` (vazia, um elemento, LIFO, pop vazia sem corromper) e `test_desfazer_lifo`.

### 9. Fila — FIFO (aula 06, slides 51–59)

- **No jogo:** Fase 2 — fila de entrada das evidências; solver — BFS.
- **No código:** `estruturas/fila.py` → `enqueue`, `dequeue`, `peek`, `esta_vazia` (dinâmica, com ponteiros `inicio` e `final`, slides 58–59).
- **A ideia:** o primeiro a entrar é o primeiro a sair. Na BFS, isso faz a busca andar "por camadas".
- **Complexidade:** O(1).
- **Prova:** `TestFila` (vazia, um elemento, ordem FIFO, intercalado; `final` volta a NULL quando a fila esvazia).

### 10. Lista ligada (aula 06, slides 6–23)

- **No jogo:** Fase 2 — lista de custódia E2 → E4 → E1 → E6; Fase 3 — cada linha da lista de adjacência do mapa.
- **No código:** `estruturas/lista_ligada.py`. Simplesmente ligada **com nó cabeça** e ponteiro `ultimo`.
- **Por que com cabeça:** "listas com cabeça não reduzem a complexidade assintótica, mas simplificam a implementação" (aula 06). Inserir ou remover no primeiro nó vira o mesmo caso dos demais.
- **Por que simplesmente ligada (pergunta do EP, 6.2):** a custódia só é percorrida do início para o fim; um ponteiro por nó basta. Custo assumido: `remover_fim` é O(n).
- **Complexidade:** inserir no início ou no fim O(1); buscar, remover e inserir no meio O(n).
- **Prova:** `TestListaLigada` (inserção e remoção no início, meio e fim; lista vazia; elemento inexistente).

### 11. Grafo e lista de adjacência (aula 09, slides 15–25)

- **No jogo:** Fase 3 — 9 locais (vértices) e 11 corredores (arestas). O EP pede pelo menos 8 e 10.
- **No código:** `estruturas/grafo.py` → `Grafo`; o mapa em `jogo/fase3.py` → `construir_mapa`.
- **A ideia:** "vetor de listas ligadas, uma para cada vértice" (aula 09). Cada vértice aponta para uma `ListaLigada` com seus vizinhos, em ordem alfabética (para a ordem de visita ser reprodutível).
- **Lista ou matriz?** Lista: o mapa é esparso (11 arestas, contra 81 células numa matriz 9×9). Com lista, BFS e DFS custam O(|V| + |E|).
- **Não orientado:** os corredores valem nos dois sentidos (cada aresta entra nas duas listas).
- **Prova:** `TestGrafo` (vizinhos repetidos ignorados, vértice isolado, destino inalcançável, mapa com ≥ 8 vértices e ≥ 10 arestas).

### 12. BFS — busca em largura (aula 09, slides 71–73)

- **No código:** `algoritmos/busca_grafo.py` → `bfs(G, s)`, linha a linha igual ao slide (cores, d, π, fila). Versão para estados: `algoritmos/solver.py` → `bfs(problema)`.
- **A ideia:** a fila garante que todos os vértices a distância 1 sejam visitados antes dos de distância 2, e assim por diante.
- **Quando a BFS acha o caminho mais curto (pergunta obrigatória do EP, 7.2):** ela encontra o caminho com **menor número de arestas** (ações). Isso equivale ao menor custo **só quando toda ação custa o mesmo** — no jogo, cada movimento custa 1. Com pesos diferentes, a BFS não garante menor custo (seria preciso Dijkstra).
- **Complexidade:** O(|V| + |E|).
- **Prova:** `test_bfs_distancias_da_aula` reproduz o exemplo dos slides 60–70: ordem s, r, w, v, t, x, u, y; distâncias s=0, r=1, w=1, v=2, t=2, x=2, u=3, y=3.

### 13. DFS — busca em profundidade (aula 09, slides 54–56)

- **No código:** `busca_grafo.dfs(G)` com `visita_dfs` recursiva (tempos d e f, cores), igual ao slide. Para estados: `solver.dfs_recursiva` e `solver.dfs_pilha`.
- **A ideia:** mergulha por um caminho até não poder mais e só então volta (backtracking).
- **Complexidade:** O(|V| + |E|) com lista de adjacência.
- **Prova:** `test_dfs_tempos` (cada vértice é descoberto antes de ser finalizado; os tempos vão de 1 a 2|V|).
- **Por que escolhemos BFS para o solver principal (pergunta do EP, seção 3):** queremos a rota de auditoria com menos movimentos, e a BFS garante isso. A DFS fica como comparação.

### 14. Estado e espaço de estados

- **No jogo:** Fase 3. Estado = **(posição, pistas, portas liberadas, energia)** — o modelo mínimo do EP (7.3).
- **No código:** `jogo/fase3.py` → `estado_inicial`, `mover` (aplica as regras R1–R5), `ProblemaMapa.sucessores`.
- **A ideia:** o grafo que o solver percorre não é o mapa, e sim o grafo de **estados**. Ele não fica guardado; os vizinhos de um estado são gerados quando necessário (grafo implícito).
- **Exemplo-chave:** a rota da BFS, A → C → E → C → B → H → D → F, passa **duas vezes por C**: a primeira sem pistas; a segunda com a pista SEQ. Mesma posição, estados diferentes.
- **Regras formais (7.5):** R1 adjacência; R2 energia ≥ 1; R3 entrar em H exige SEQ; R4 entrar em F exige AUT; R5 pistas coletadas ao chegar em E e D.
- **Prova:** `TestRegrasFase3` — cenário 1 (A-C-G-F, o caminho mais curto em arestas, é recusado: falta AUT) e cenário 2 (A-B-H recusado: falta SEQ).

### 15. Árvore de busca (item 9.2)

- **No código:** `solver.Resultado.arvore` (lista de arestas pai → ação → filho) e `desenhar_arvore_de_busca`.
- **A ideia:** cada nó é um estado; cada aresta, a ação que levou a ele. A árvore cresce a cada estado expandido. Com b ações possíveis por estado e profundidade d, ela pode chegar a b^d nós — por isso explorar tudo fica caro, e o controle de repetidos (AVL) é essencial.
- **Por que o solver para na primeira solução:** o objetivo é *encontrar* uma rota válida. Com a BFS, a primeira encontrada já é a de menos ações; explorar o resto não melhoraria a resposta.
- **Para mostrar:** Resolver → Fase 3 → BFS (árvore em texto) ou visualização → aba Árvore de busca (BFS fica larga e rasa; DFS, estreita e funda).

### 16. Árvore AVL (aula 08)

- **No jogo:** Fase 4, Sala 1 — o jogador prevê a rotação antes de cada inserção.
- **No código:** `estruturas/avl.py` → `_rotacao_direita` (RD), `_rotacao_esquerda` (RE), `_rotacao_esquerda_direita` (RED), `_rotacao_direita_esquerda` (RDE), `_insere`, `buscar`. Altura guardada no nó; árvore vazia tem altura −1; FB = hE − hD.
- **A ideia:** numa árvore de busca comum, inserir chaves em ordem cria uma "lista" de altura n. A AVL corrige a altura a cada inserção, com rotações O(1), e mantém **altura O(log n)**.
- **Complexidade:** busca e inserção O(log n) — proporcionais à altura. Medido: 10.000 chaves inseridas em ordem → altura 13 (log₂ 10.000 ≈ 13,3).
- **Prova:** `test_exemplo_da_aula` usa a sequência dos slides 9–15 (70, 50, 40, 80, 90, 15, 25, 45, 42) e confere as 4 rotações, na ordem e nos nós dos slides, e a árvore final. Também: chave duplicada recusada, busca existente e inexistente.
- **Evidência técnica (8.3):** a Sala 1 e a aba AVL mostram a árvore antes e depois de cada rotação, com h e FB.

### 17. Chave de estado e controle de visitados (Fase 4)

- **No código:** `jogo/fase3.py` → `chave_estado` e `algoritmos/solver.py` → `_Visitados`.
- **A ideia:** antes de explorar um estado, o solver pergunta à AVL "já vi esta chave?". A chave é **(posição, pistas, portas)**. A energia fica guardada como valor, com a regra de **dominância**: um estado repetido com energia menor ou igual não é explorado de novo; com mais energia, substitui o anterior.
- **Por que a energia não entra na chave:** com as mesmas pistas e portas, ter menos energia nunca permite fazer algo novo. Incluir a energia multiplicaria o número de estados por até 11.
- **Enigma 8.2 ("o estado que parece igual"):** Sala 2 da Fase 4. As respostas certas são **calculadas** por `chave_estado` e pela dominância, não escritas à mão.
- **Prova:** `test_mesma_posicao_pistas_diferentes_sao_estados_diferentes`, `test_estados_repetidos_nao_sao_expandidos`, `test_sala2_respostas_calculadas`. No mapa padrão, a AVL barrou 24 estados repetidos na BFS.

### 18. Solver integrado às regras

- **No código:** `algoritmos/solver.py` → `bfs`, `dfs_recursiva`, `dfs_pilha`. Funcionam com qualquer "problema" que tenha `estado_inicial`, `sucessores`, `eh_objetivo`, `chave` e `recurso`. A Fase 2 (`ProblemaTriagem`) e a Fase 3 (`ProblemaMapa`) usam as mesmas funções de regra do jogador.
- **Métricas (RF10):** caminho, custo, estados expandidos, gerados, repetidos, fronteira máxima (tamanho da fila ou pilha), nós/altura/rotações da AVL, tempo.
- **Prova:** `test_todas_as_estrategias_respeitam_as_regras` refaz cada passo da solução com `mover()`; `test_solver_resolve_fase2` refaz a solução no jogo manual; `test_manual_e_solver_chegam_ao_mesmo_estado_final`.

### 19. Testes e análise de complexidade

- **Onde:** `testes/` (104 testes, um arquivo por módulo, cobrindo a tabela da seção 15) e `experimentos.py` → `docs/metricas.md`.
- **Como rodar:** `rodar_testes.bat` (dois cliques) ou `py -m unittest discover -s testes -t .`.
- **Teoria × experimento:** as contagens confirmam a teoria das aulas (Bubble n(n−1)/2; Quick no pior caso n(n−1)/2; AVL com altura ≈ log₂ n). Os tempos dependem da máquina; as contagens, não.
- **Um erro real encontrado por teste de integração:** a Fase 5 lia o histórico da Fase 2 num formato errado. Uma partida simulada do início ao fim revelou o erro; ele foi corrigido e virou o teste `test_integracao_com_o_historico_real_das_fases_2_e_3`.

### 20. Narrativa, modularização e interface

- **Jogar sem ajuda (pedido da professora):** cada tela de fase mostra ">> O QUE FAZER AGORA", que muda conforme a situação; a tecla **?** dá uma dica; o jogo aceita a palavra da ação além do número ("guardar" ou "2"), sem diferenciar maiúsculas nem acentos. Guia de uma página em `COMO-JOGAR.md`, também exibido na opção Instruções.
- **Dicas calculadas pelo solver:** nas Fases 2 e 3, a dica é o primeiro passo do caminho que a BFS encontra a partir da situação atual do jogador (`jogo/dicas.py`). Seguir as dicas sempre vence a fase (`testes/test_dicas.py`); se não houver caminho (ex.: energia insuficiente), a dica manda desfazer.

- **Narrativa:** `jogo/narrativa.py` é a fonte única da história (prólogo, capítulos, epílogo), usada pelo terminal e pela visualização. Cada fase tem a mensagem de abertura do enunciado e um selo; os 5 selos abrem o Cofre de Verificação.

- **Separação (seção 12):** `estruturas/` não sabe nada do jogo; `algoritmos/` não sabe nada da tela; `jogo/` tem as regras; `interface/` só mostra e lê opções. Por isso as mesmas regras servem ao jogador, ao solver, aos testes e à visualização.
- **Feedback:** toda jogada recusada explica o motivo e não altera nada (seção 6.4).

---

## Parte 3 — Bônus (seção 18 do EP)

| Bônus do EP | Situação | Onde |
|---|---|---|
| Visualização animada da fila, pilha, lista, AVL e árvore de busca | **Feito** | `visualizar.bat` ou menu → 5; `interface/visualizacao.py` |
| Geração procedural de mapas com seed | **Feito** | `jogo/cenarios.py` → `gerar_mapa` |
| Gerador de enigmas com verificador automático de solução | **Feito** (para mapas) | `gerar_mapa` só entrega mapas que a BFS consegue resolver |
| Níveis de dificuldade com mais vértices e estados | **Parcial** | Mapas de 30 e 60 vértices nos experimentos; não são selecionáveis no menu |
| Editor de fases sem alterar o código | Não feito | — |
| Heurística (ex.: A\*) comparada a BFS/DFS | Não feito | — |
| Modo cooperativo | Não feito | — |
| Fila de prioridade | Não feito (há heap na aula 08) | — |

### B1. Visualização animada — "Audiência Pública da CIV"

- **O que é:** uma página HTML única (`visualizacao.html`), que abre no navegador **sem internet** e sem bibliotecas externas. Funciona em **modo slides** (setas do teclado, para projetar) e em **modo leitura** (rolagem).
- **A história:** Miss Pearl, Analista de Integridade de Dados da CIV, presta contas à população de Verídia em nome da equipe (mestrandos da turma 2026, orientados pela Profa. Dra. Lucy) — o que aconteceu e *como* a trilha foi reconstruída. O desafio é exatamente o do enunciado (mesmas fases, enigmas, regras e selos); muda só quem conta e a linguagem.
- **Para quem:** camada principal para jovens (9.º ano), com analogias do cotidiano, e uma **ficha técnica dobrável** em cada anexo para a banca (termo da disciplina, complexidade, código e teste).
- **Estrutura de cada anexo (fase):** o problema → como pensamos (analogia) → **sua vez** (palpite ou jogo) → o que a máquina fez (animação real) → a prova (carimbo "Conferido").
- **Personagens (originais):** Miss Pearl, narradora; APURA-42, o computador da CIV, que reage aos palpites. A Profa. Dra. Lucy aparece apenas como crachá de orientadora, sem retrato.
- **Glossário** no início: auditoria, trilha, registro, zona e seção, evidência, cadeia de custódia, lacre, selo, cofre, consistente, apuração — cada termo com o significado em linguagem simples.
- **Analogias da trilha reversa:** slide "De onde veio este número?" (o caminho genérico de um voto — seção, zona, boletim, resultado — e o espelho em Verídia) e slide "As migalhas de João e Maria": cada estado guarda o pai π; para reconstruir a rota, segue-se π do destino até a origem e inverte-se a lista (`busca_grafo.caminho`, `solver._reconstruir`).
- **Mais recursos visuais:** onda da BFS por camadas no mapa (d[v] da aula 09), gráfico de barras das comparações (500 fichas), ícones de fila, pilha, lista e arquivo.
- **Jogável na página:** a Fase 2 inteira e a Fase 3 inteira. O Python calcula **todas** as situações possíveis (14 na triagem, 160 no mapa) e o resultado de cada jogada, com as mesmas funções de regra do jogo; a página só consulta essas tabelas (`dados_triagem_jogavel`, `dados_mapa_jogavel`).
- **Animações reais:** ordenação das 12 fichas do lote (Bubble, Merge, Quick), mapa de todas as situações da triagem, BFS × DFS no mapa, árvore de busca, AVL antes/depois com palpite de rotação, pares do enigma 8.2, relatório da Fase 5.
- **Prova:** `testes/test_visualizacao.py` (página sem referências externas; dados batem com a execução; jogos da página seguem as regras do Python; animação sem fichas duplicadas).

### B2. Gerador de mapas com verificador

- **Como garante que o mapa é conexo:** sorteia primeiro uma **árvore geradora** — cada novo vértice se liga a um já existente. Uma árvore com n vértices tem n − 1 arestas e liga todos. Depois acrescenta arestas extras, que criam ciclos e rotas alternativas.
- **Como garante que há solução:** sorteia onde ficam pistas e portas e roda a BFS. Se não houver solução, tenta a próxima seed.
- **Resultado útil para a análise:** no mapa de 30 vértices, a BFS encontra 7 ações e a DFS, 35. No de 60 vértices, a DFS expandiu **mais** estados que a BFS (235 × 181): a DFS não garante explorar menos.
- **Prova:** `TestCenarios` (mesma seed → mesmo mapa; mapa conexo; sempre com solução).

---

## Parte 4 — Perguntas prováveis e respostas curtas

| Pergunta | Resposta |
|---|---|
| Por que BFS no solver? | Queremos a rota com menos movimentos; como cada movimento custa 1, a BFS garante isso. |
| A BFS acha o menor custo? | Só se todas as ações custarem o mesmo. Com pesos diferentes, não. |
| Por que AVL e não lista para os visitados? | Na lista, cada consulta custa O(n); na AVL, O(log n). O solver consulta a cada estado gerado. |
| Por que a energia não está na chave? | Dominância: mesmo lugar, mesmas pistas e portas, com menos energia, nunca é melhor. Evita multiplicar os estados. |
| Dois estados na mesma posição são iguais? | Não, se as pistas ou portas forem diferentes: permitem ações diferentes (C sem SEQ × C com SEQ). |
| Por que lista com cabeça? | Simplifica inserção e remoção no início; mesma complexidade (aula 06). |
| Por que simplesmente ligada? | A custódia só é percorrida para a frente; um ponteiro basta. |
| Por que lista de adjacência? | Grafo esparso; BFS/DFS em O(V + E). |
| O Quick Sort do slide funciona? | Com `p..q`, entra em laço quando o pivô é o maior; usamos `p..q−1`, e há teste demonstrando. |
| Por que o id no fim da chave? | Merge (da aula) e Quick não são estáveis; o id torna a ordem final única. |
| A resposta está escrita no código? | Não. As regras são funções; o solver explora estados a partir delas. A Fase 5 reexecuta as jogadas do jogador e recusa trilhas inválidas (ex.: A-C-G-F). |
| Como sei que a AVL está balanceada? | `eh_avl()` confere todos os nós; o teste verifica após cada inserção. Altura 13 com 10.000 nós. |
| O que acontece com jogada inválida? | É recusada com explicação; nenhum dado muda (testado em todas as fases). |
