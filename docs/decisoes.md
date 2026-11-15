# Decisões do EP "Urna Lógica"

Registro das escolhas de projeto, com a justificativa de cada uma. Serve para retomar o trabalho em qualquer conversa e para o aluno defender as decisões.

Legenda: **[Aula]** = segue o material da disciplina · **[EP]** = exigido no enunciado · **[Equipe]** = escolha da equipe, a justificar na apresentação.

## Contexto

- Equipe: 1 aluno (apresenta) + IAG (Claude) como programador. Aluno sem prática recente de programação.
- Prazo: demonstração por volta de 19.11.2026, em notebook próprio (Windows, Python 3.14), **sem internet**.
- Cópias: GitHub privado `perlalacerda/urna-logica` e pasta no Google Drive.

## Tecnologia

| Decisão | Origem | Justificativa |
|---|---|---|
| Python 3, só biblioteca padrão | [Aula] [Equipe] | Aula 00 indica EP "com Python"; sem `pip`, roda offline |
| Jogo em terminal + páginas HTML offline para visualização | [Equipe] | Terminal é o modo seguro; HTML entra como bônus de visualização |
| Testes com `unittest` | [Equipe] | Já vem no Python; `python -m unittest` |
| Nomes em português, iguais aos do pseudocódigo das aulas | [Equipe] | O aluno reconhece no código o que viu no slide |

## Estruturas de dados

| Estrutura | Escolha | Origem | Justificativa |
|---|---|---|---|
| Lista ligada | Simplesmente ligada **com cabeça**, mais ponteiro para o último nó | [Aula] [Equipe] | Cabeça simplifica inserção/remoção (aula 06); ponteiro `ultimo` deixa a inserção no fim O(1), usada na lista de custódia |
| Pilha | Dinâmica (nós ligados) | [Aula] | push/pop O(1), sem limite MAX |
| Fila | Dinâmica (inicio/final) | [Aula] | enqueue/dequeue O(1) |
| Operações em estrutura vazia | Devolvem `(False, None)` em vez de erro | [Aula] [EP] | Igual ao `retorna false` dos slides; atende "remoção em estrutura vazia sem falha inesperada" |
| AVL | Altura guardada no nó, árvore vazia = -1, FB = hE - hD | [Aula] | Igual às aulas 07 e 08 |
| AVL com chave repetida | Recusada (devolve "já existe") | [Equipe] | No EP, chave repetida = estado já visitado |

## Algoritmos

| Algoritmo | Escolha | Origem |
|---|---|---|
| Bubble Sort | Iterativo do slide 10 (aula 02); versão recursiva também disponível | [Aula] |
| Merge Sort | Do slide 21 (aula 02), com a metade direita invertida em B | [Aula] |
| Quick Sort | Particiona de Lomuto (pivô = último), recursão em `p..q-1` e `q+1..r` | [Aula] com correção — ver abaixo |
| Comparação | Chave composta (zona, seção, horário, id_registro) | [EP] [Equipe] |
| BFS / DFS | Exatamente como na aula 09 (cores, d, π, tempo) | [Aula] |

### Correção no Quick Sort
O slide 31 da aula 04 chama `quickSort(A, p, q)`. Com o particiona de Lomuto, se o pivô for o maior valor, q = r e a mesma chamada se repete indefinidamente. Adotou-se `quickSort(A, p, q-1)` (Cormen, 4.ª ed.). Há teste que demonstra o problema. **Pendente:** confirmar com a professora.

### Desempate pelo id_registro
O enunciado (5.3) pede zona → seção → horário. Merge (versão da aula) e Quick **não são estáveis**; sem desempate, registros com a mesma chave podem sair em ordem diferente em cada algoritmo, e o teste "comparar resultado dos três algoritmos" falharia. Acrescentar `id_registro` (único) como último critério torna a ordem final única.

## Regras das fases

- **Fase 2 (adotado, documentado):** ações aceitar, guardar, arquivar, liberar e desfazer.
  - **arquivar** dá destino a E3 e E5, que não fazem parte da custódia. [Equipe]
  - **guardar** só aceita uma evidência que precise sair *antes* da que está no topo. Isso impede "enterrar" uma evidência na pilha (beco sem saída). [Equipe]
  - **desfazer** guarda na pilha do histórico uma "foto" do estado antes de cada ação válida; desfazer restaura a foto mais recente (LIFO). [Equipe]
  - O espaço de estados completo tem 14 estados e 1 estado objetivo (verificado por busca em largura). Pequeno o bastante para desenhar na apresentação.
- **Fase 1:** o gerador sorteia poucos horários (cerca de n/3) para garantir horários repetidos em zonas diferentes, condição do enigma 5.3. Lote padrão: seed 2042, 12 registros.
- **Fase 3 (adotado):** mapa final com 9 vértices e 11 arestas, não orientado, em lista de adjacência feita de listas ligadas (aula 09). [EP] [Aula] [Equipe]
  - O enunciado chama E de "Unidade Oeste" (7.1) e cita um "Arquivo Oeste" (7.5). Resolvido criando os dois: **E = Unidade Oeste** (guarda a pista SEQ) e **H = Arquivo Oeste** (porta que exige SEQ). Assim a regra deixa de ser circular. [Equipe]
  - Ponto de autenticação: D (pista AUT). A porta de F exige AUT, o que força passar por D antes do Centro de Validação. [EP 7.5]
  - Caminho mais curto em arestas: A-C-G-F (3), **inválido** pelas portas. Rota válida encontrada pelo solver: A-C-E-C-B-H-D-F (7). Passa duas vezes por C, com pistas diferentes: exemplo direto de "mesma posição, estado diferente". [EP 7.5, 8.2]
  - Energia inicial 10; cada movimento custa 1. Com energia 6, não há solução (teste).
- **Estado e chave da AVL (Fase 4):** estado = (posição, pistas, portas, energia). A chave da AVL é (posição, pistas, portas); a energia é guardada como valor e usada por **dominância**: um estado repetido com energia menor ou igual não é expandido; com energia maior, substitui o anterior. Justificativa: com as mesmas pistas e portas, ter menos energia nunca permite fazer algo novo. Evita multiplicar o número de estados por (energia + 1). [Equipe]
- **Solver:** BFS (fila própria), DFS recursiva (pilha de chamadas) e DFS com pilha própria, todas usando as mesmas funções de regra do modo manual. O dicionário `pais` serve apenas para reconstruir o caminho; o controle de visitados é feito exclusivamente pela AVL. [EP] [Equipe]

- **Fase 4 (adotado):** três salas. Sala 1: o jogador prevê a rotação antes de cada inserção, com a sequência do exemplo da aula 08 (70, 50, 40, 80, 90, 15, 25, 45, 42), que provoca RD, RE, RED e RDE; árvore desenhada antes e depois, com h e FB. Sala 2: enigma 8.2 com 4 pares de estados; as respostas certas são calculadas por `chave_estado()` e pela regra de dominância do solver, não escritas à mão. Sala 3: busca existente e inexistente, com o caminho na árvore. Selo 4 = Sala 1 completa + Sala 2 toda correta. [EP 8] [Aula] [Equipe]
- **Fase 5 (adotado):** etapas lote → triagem → mapa → relatório. Se o jogador resolveu as Fases 2 e 3, suas ações são reexecutadas e conferidas pelas regras; senão, a BFS resolve. A tabela BFS × DFS do relatório é ordenada com Merge Sort (item 9.3). Selo 5 = as três etapas consistentes; com os 5 selos, abre-se o Cofre de Verificação. [EP 9]
- **Cenários de comparação:** cenário 1 = mapa padrão; cenário 2 = mapa de 30 vértices gerado por seed (árvore geradora + arestas extras), com verificador automático de solução por BFS (bônus "geração procedural" e "gerador com verificador"). [EP 9.1, 18]

- **Visualização (bônus "visualização animada"):** `interface/visualizacao.py` executa os algoritmos reais, grava cada passo (fronteira da BFS/DFS, AVL antes/depois, estruturas da Fase 2, escritas no vetor) e embute os dados num único `visualizacao.html`, sem bibliotecas nem internet. Seis abas: mapa e busca, árvore de busca, AVL, triagem, ordenação, métricas. [EP 18] [Equipe]

- **Audiência Pública (visualização):** narradora Miss Pearl e mascote APURA-42, personagens originais; estética retrofuturista própria (sem elementos da TVA/Marvel; pedido de usar a Senhorita Minutos como referência foi recusado por ser personagem protegido). A Profa. Dra. Lucy aparece só como crachá de orientadora, sem retrato. A analogia da vida real descreve o caminho genérico de um voto, sem locais nem números reais, porque o enunciado proíbe dados de eleições reais. [Equipe]

- **Desafio extra — mapa com custos (aula 11, adotado):** variante da Fase 3 com os mesmos locais, pistas e portas e custos por corredor (A-B 1, A-C 6, B-C 1, B-H 2, B-I 2, C-E 1, C-G 2, D-F 2, D-H 2, F-G 5, G-I 1), energia 15. Os pesos foram escolhidos para que, no mesmo mapa, a BFS (7 movimentos, 15 de energia), o guloso ingênuo (trava) e o Dijkstra (8 movimentos, 11 de energia) deem respostas diferentes. A Fase 3 original e o selo 3 não mudam; o desafio não dá selo. Base no EP: item 7.4 ("custo definido por você") e item 7.2 (BFS × pesos). [EP 7.2, 7.4] [Aula 11] [Equipe]
- **Heap e Dijkstra:** heap de mínimo próprio, adaptado do heap de máximo da aula 08 (comparações invertidas), com `diminuir_chave` para o relaxamento. O `dijkstra()` literal da aula roda no grafo puro; o `dijkstra_estados()` roda no grafo implícito de estados, com Q começando só com o estado inicial e S guardado na AVL. A energia sai do vértice porque energia restante = energia inicial − d. O guloso ingênuo proíbe voltar a um estado já visitado (senão andaria em círculo) e desempata pela ordem alfabética dos vizinhos. [Aula 08] [Aula 11] [Equipe]
- **Tecla da tabela no desafio extra:** T, e não C, porque C é um local do mapa (mesmo problema que levou a dica da Fase 3 a usar ? em vez de D). [Equipe]

- **Jogo no navegador fácil e divertido (pedido da professora, adotado em 14.11.2026):** tela inicial curta, cartão de instruções por fase, carimbo, animações e estrelas. As estrelas são só apresentação: as regras e os mínimos (BFS 7, Dijkstra 11) continuam vindo do Python. Na Fase 1 do navegador, a jogadora monta a chave composta com peças em vez de escolher um critério pronto, porque o 4.º critério repetia o texto do enigma e entregava a resposta. O terminal mantém os critérios fixos. [Equipe]

- **Modo aluno 9.º ano (15.11.2026):** a jogabilidade foi revista a partir da avaliação da Perla jogando como a professora (termos sem tradução, Fase 3 sem entender como jogar, Fase 4 longa demais, Fase 5 sem explicar a escolha do método, falta de "próxima fase"). Os termos do jogo ganharam nomes lúdicos (esteira, pilha de espera, cofre de custódia, arquivo morto) e cada um leva ao conceito da aula. Os nomes do código (aceitar, guardar, arquivar, liberar) continuam nas regras completas, para a banca ligar tela e código. A tradução do custo usa "1 segundo por comparação" como ilustração, não como medida real. [Equipe]

## Pendências com a professora

1. Quick Sort: `p..q` do slide × `p..q-1`.
2. Fase 2: ação "arquivar" (adotada; confirmar se a professora aceita).
3. Fase 3: "Unidade Oeste" × "Arquivo Oeste" (adotados como dois locais distintos).
4. Bônus "editor de fases": fases em arquivo JSON contam?
5. A professora concorda em aparecer, pelo nome, como orientadora na Audiência Pública?
