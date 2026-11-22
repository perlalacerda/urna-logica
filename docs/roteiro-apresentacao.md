# Roteiro de apresentação — Urna Lógica

Roteiro para a demonstração em sala: uma partida manual, uma execução do solver e a ligação de cada passo com os conceitos da disciplina (seção 16 do EP).

**Duração-base: 20 minutos.** O enunciado não informa o tempo da apresentação; os blocos têm duração indicada para cortar ou estender conforme o tempo real. Os blocos marcados ★ são essenciais.

Material de apoio: `docs/guia-codigo-conceitos.md` (cartões por conceito e perguntas prováveis) e `docs/metricas.md` (números).

---

## Antes de começar (10 minutos antes)

- [ ] Notebook ligado na tomada; modo avião não atrapalha (nada usa internet).
- [ ] Pasta do projeto aberta no Explorador.
- [ ] Rodar `rodar_testes.bat` uma vez: precisa terminar em `OK` (138 testes).
- [ ] Rodar `visualizar.bat`: deixar a página aberta no navegador, na aba "Mapa e busca".
- [ ] Abrir `jogar.bat` e deixar no **menu inicial** (sem jogar: os selos começam vazios).
- [ ] Abrir no editor (Bloco de Notas ou VS Code) os arquivos que serão mostrados:
  `estruturas/avl.py`, `algoritmos/busca_grafo.py`, `jogo/fase3.py`, `algoritmos/ordenacao.py`.
- [ ] Aumentar a fonte do terminal (Ctrl + roda do mouse) para a sala enxergar.
- [ ] Ter este roteiro impresso ou numa segunda tela.

---

## Bloco 1 ★ — Abertura: a história e a arquitetura (2 min)

**Mostrar:** a visualização na aba **"A missão"** (prólogo e os 5 selos). Ler em voz alta o primeiro e o último parágrafo do prólogo.
> "Ano 2042: uma falha embaralhou a auditoria de Verídia. Sou Analista de Integridade de Dados da CIV, uma comissão apartidária. A pergunta é: dá para reconstruir a trilha da apuração respeitando todas as regras? Cada selo exige um conceito da disciplina."

Depois, ir para o terminal com o **menu inicial do jogo** (o mesmo prólogo aparece ao abrir o jogo).

**Fala sugerida:**
> "O jogo é uma investigação fictícia em Verídia: cinco fases, cada uma com um selo. A ideia central do projeto é que **cada fase é um problema de busca**: um estado inicial, ações válidas e um objetivo. O jogador escolhe as ações; o solver explora sozinho. E os dois usam **as mesmas funções de regra** — por isso o solver não tem resposta pronta."

**Mostrar rapidamente:** as pastas `estruturas/`, `algoritmos/`, `jogo/`, `interface/`, `testes/`.
> "Separei estruturas, algoritmos, regras e tela. Tudo foi implementado por nós, em Python puro, sem bibliotecas — e cada função traz no comentário o pseudocódigo do slide da aula."

---

## Bloco 2 ★ — Fase 1: ordenação e chave composta (3 min)

**Ações no jogo:** Jogar → 1.
1. Opção 1 (ver o enigma) e ler em voz alta: zona, depois seção, depois horário.
2. Opção 2 → Merge Sort → critério **"horário"**. O jogo recusa e mostra as duas linhas onde a ordem quebra.
   > "Ordenar só pelo horário não basta: há registros com o mesmo horário em zonas diferentes."
3. Opção 3 (comparar 10, 100, 500) — antes de ganhar o selo, porque o selo encerra a fase.
   > "Com 500 registros, o Bubble faz 124.750 comparações — exatamente n(n−1)/2 — e o Merge, cerca de 4.500. É a diferença entre Θ(n²) e Θ(n log n) da aula 04."
4. Opção 2 → Quick Sort → critério **"auditoria"**. Selo 1.
   > "A regra virou uma chave composta: a tupla (zona, seção, horário, id). Python compara campo a campo, como num dicionário."

**Se perguntarem por que o id no fim:** Merge (da aula) e Quick não são estáveis; o teste `test_estabilidade` mostra isso.

**Achado para destacar (30 s):** abrir `algoritmos/ordenacao.py` em `quick_sort`.
> "O slide chama `quickSort(p, q)`. Com o particiona de pivô no fim, se o pivô for o maior valor, a chamada se repete para sempre. Usamos `p..q−1`, como no Cormen, e deixamos um teste que demonstra o laço."

---

## Bloco 3 ★ — Fase 2: fila, pilha e lista ligada (3 min)

**Ações no jogo:** Fase 2.
1. Tentar **1 (aceitar)** logo de início → recusado: "a custódia espera E2, não E1".
   > "A fila só libera o primeiro: FIFO. Jogada inválida é recusada com explicação e não altera nada."
2. **2 (guardar)** E1 na pilha → **1** aceitar E2 → **3** arquivar E3 → **1** aceitar E4.
3. **5 (desfazer)** → volta E4 para a fila. Depois **1** de novo.
   > "O desfazer é uma pilha: a cada ação guardo uma foto do estado; desfazer restaura a mais recente. LIFO."
4. **4 (liberar)** E1 → **3** arquivar E5 → **1** aceitar E6. Selo 2.
   > "A custódia é uma lista ligada com nó cabeça, como na aula 06: o cabeça simplifica inserir no início."

**Se perguntarem por que simplesmente ligada:** a custódia só é percorrida para a frente; um ponteiro basta.

---

## Bloco 4 ★ — Fase 3: grafo, estado e a armadilha do caminho curto (3 min)

**Ações no jogo:** Fase 3.
1. Mostrar o mapa (lista de adjacência na tela).
   > "O mapa é um grafo não orientado em lista de adjacência — um vetor de listas ligadas, como na aula 09. 9 vértices, 11 arestas."
2. Digitar **M**: a BFS no grafo puro dá A → C → G → F (3 arestas).
3. Tentar esse caminho: **C**, **G**, **F** → recusado na porta de F: falta a pista de autenticação.
   > "O caminho mais curto em arestas é inválido. Por isso o estado não pode ser só a posição: é posição, pistas, portas e energia."
4. **R** (reiniciar) e fazer a rota válida: **C, E, C, B, H, D, F**. Selo 3.
   > "Passei duas vezes por C: na primeira sem pistas, na segunda com SEQ. Mesma posição, estados diferentes."

---

## Bloco 5 ★ — Solver: BFS × DFS e árvore de busca (3 min)

**Ações:** voltar ao menu → **2 (Resolver)** → **2 (mapa)** → **4 (comparar)**.
> "A BFS acha 7 ações; a DFS, 9. A BFS garante o menor número de ações porque cada movimento custa 1. Com pesos diferentes, isso não valeria."

**Trocar para o navegador** (visualização), aba **Mapa e busca**:
1. Estratégia BFS → **tocar**. Apontar a FILA crescendo pelo final.
2. Estratégia DFS com pilha → **tocar**. Apontar a PILHA crescendo pelo topo.
   > "Mesmo código de regras, só muda a estrutura: fila explora por camadas; pilha mergulha em profundidade."
3. Aba **Árvore de busca**: BFS (larga e rasa) × DFS (estreita e funda).

**Recursão (se der tempo, 30 s):** abrir `algoritmos/solver.py` em `dfs_recursiva` e apontar os comentários: caso-base 1 (objetivo), chamada recursiva, caso-base 2 (beco sem saída).

---

## Bloco 5b — Desafio extra: algoritmos gulosos (aula 11) (2 min)

**Ações (navegador):** menu → cartão **Desafio extra** → clicar **C** (o atalho).
> "Mesmo mapa da Fase 3, mas agora cada corredor gasta uma energia diferente. O atalho A-C está em obras: custa 6."
1. **Recomeçar** → **💡 Dica (Dijkstra)** → seguir B, C, E, C, B, H, D, F. Mensagem: "gastou 11 … Rota ótima".
2. Rolar até **Compare: quem gasta menos?**
   > "A BFS acha 7 movimentos, mas gasta 15: ela conta arestas, não custo. O Dijkstra dá 8 movimentos e gasta 11."
3. Clicar **Ver rota: Guloso**.
   > "O guloso ingênuo pega sempre o corredor mais barato e nunca volta atrás. Cada passo parece bom, mas ele trava na Central — como o troco de 19 com moedas 2, 3 e 6."
4. Abrir **Passo a passo do Dijkstra da aula**: apontar o Extrai-Min e o relaxamento.
   > "O Dijkstra também é guloso: escolhe sempre o menor d[u], tirado de um heap de mínimo (aula 08). Com pesos não negativos, essa escolha é segura. Complexidade O((V + E) log V)."

**Se perguntarem do código:** `algoritmos/dijkstra.py` (pseudocódigo da aula 11 linha a linha) e `estruturas/heap.py` (subir e descer da aula 08).

---

## Bloco 6 ★ — Fase 4: AVL e chave de estado (3 min)

**Ações no jogo:** Fase 4 → Sala 1. Inserir os lacres prevendo a rotação; parar nas inserções que giram:
- **40 → RD** ("reta" à esquerda), **90 → RE**, **25 → RED** ("curva"), **42 → RDE**.
> "É exatamente a sequência do exemplo da aula 08. Depois de cada inserção o jogo explica: qual nó ficou com FB ±2 e por que aquela rotação."

**Alternativa mais rápida:** visualização → aba **AVL** → avançar até a inserção 7 (antes e depois lado a lado).

Inserir **todos os 9 lacres** (previsões erradas não impedem o selo; só a Sala 1 incompleta impede).

**Sala 2 — responder os 4 pares** (o Selo 4 exige todos certos). Comentar só o 1.º e o 2.º; responder os outros rapidamente:

| Par | a) mesma chave? | b) explorar o novo? | Por quê |
|---|---|---|---|
| 1. C sem pistas × C com SEQ | n | s | pistas diferentes = chaves diferentes |
| 2. B {SEQ} energia 6 × energia 4 | s | n | mesma chave, menos energia: repetido |
| 3. D energia 4 × energia 6 | s | s | mesma chave, MAIS energia: explora de novo |
| 4. H × B | n | s | posições diferentes |

> "Mesma posição C, com e sem SEQ: chaves diferentes. Mesma chave com menos energia: repetido, o solver não expande. A AVL guarda (posição, pistas, portas) e a energia vai como valor — regra de dominância."

**Número para citar:** 10.000 chaves inseridas em ordem → altura 13 (log₂ 10.000 ≈ 13,3). Uma árvore de busca comum teria altura 9.999.

---

## Bloco 7 ★ — Fase 5: auditoria final (1,5 min)

**Ações:** Fase 5 → escolher Merge Sort.
> "A Fase 5 não aceita nada porque sim: refaz as minhas jogadas das Fases 2 e 3 com as regras e confere. Depois compara BFS e DFS em dois cenários — o segundo é um mapa de 30 locais gerado por seed — e ordena a tabela com Merge Sort, como pede o item 9.3."

Fechar a história na visualização, aba **"5 · Auditoria Final"**, quadro **Cofre de Verificação aberto** (epílogo).

Apontar no relatório: **CONSISTENTE** nas três etapas, a tabela BFS × DFS (7 × 35 ações no cenário 2) e a mensagem do **Cofre de Verificação aberto**.

---

## Bloco 8 — Testes, métricas e bônus (1 min)

- Mostrar o resultado de `rodar_testes.bat`: **138 testes, OK**.
  > "Os testes cobrem a tabela da seção 15: estrutura vazia, um elemento, vários, inválidos, rotações, BFS com a ordem do exemplo da aula, integração manual × solver."
- Citar um teste que pegou erro real: a Fase 5 lia o histórico da Fase 2 no formato errado; a partida simulada revelou; virou teste.
- Bônus feitos: visualização animada offline; gerador de mapas por seed com verificador de solução. No mapa de 60 locais, a DFS fez **mais** expansões que a BFS (235 × 181), embora tenha visto menos chaves distintas (93 × 218): ela reexpande uma chave quando volta com mais energia. A DFS não garante explorar menos.

---

## Bloco 9 ★ — Uso de IAG (30 s)

> "Usei IA generativa como programador assistente. Tudo está registrado no relatório de uso de IA: o que foi pedido, o que foi aproveitado e como validei. A validação foi por testes, pela comparação com os slides e por jogar o jogo. Dois exemplos de curadoria: a correção do Quick Sort do slide e o erro de integração da Fase 5."

**Atenção:** a coluna "Como foi validado" do registro precisa ser preenchida **pelo aluno**, com o que ele mesmo conferiu.

---

## Plano B (se algo falhar)

| Problema | Saída |
|---|---|
| `jogar.bat` não abre | Abrir a pasta, clicar na barra de endereço, digitar `cmd`, Enter, e rodar `py jogo.py` |
| Comando de testes dá erro | Conferir se está **dentro** da pasta `urna-logica` e se o comando termina com `-t .` (com o ponto) |
| Navegador não abre a visualização | Dar dois cliques em `visualizacao.html` na pasta do projeto |
| Errou uma jogada na demonstração | Usar **desfazer** (Fase 2: 5; Fase 3: U) — e aproveitar para mostrar a pilha |
| Tempo acabando | Pular para o Bloco 7 (Fase 5) com o solver resolvendo as fases não jogadas |
| Professora quer jogar | Abrir `jogar_navegador.bat` (tela inicial com ▶ Começar, cartão "Como jogar em 10 segundos" em cada fase, botão 💡 Dica, estrelas por fase) ou entregar o `COMO-JOGAR.md` impresso e deixá-la jogar a Fase 2 ou a 3. Se travar, ela digita **?** e recebe a dica calculada pelo solver |

---

## Divisão do tempo

| Bloco | Tema | Minutos |
|---|---|---|
| 1 ★ | Abertura e arquitetura | 2 |
| 2 ★ | Fase 1 — ordenação | 3 |
| 3 ★ | Fase 2 — fila, pilha, lista | 3 |
| 4 ★ | Fase 3 — grafo e estado | 3 |
| 5 ★ | Solver — BFS × DFS | 3 |
| 5b | Desafio extra — gulosos (aula 11) | 2 |
| 6 ★ | Fase 4 — AVL | 3 |
| 7 ★ | Fase 5 — auditoria | 1,5 |
| 8 | Testes, métricas, bônus | 1 |
| 9 ★ | IAG | 0,5 |
| | **Total** | **22** (20 sem o 5b) |

Para **10 minutos**: blocos 1, 2 (só passo 4), 4 (só passos 2–3), 5 (só a visualização), 6 (só a aba AVL), 7 e 9.

---

## Versão "Audiência Pública" (turma do 9.º ano, ~25 min)

Abrir `visualizar.bat`, deixar em **tela cheia** (F11) e avançar com as setas. A apresentadora fala como **Miss Pearl**, Analista de Integridade de Dados da CIV; o APURA-42 é o computador que "pede o palpite".

| Slides | Momento | O que fazer |
|---|---|---|
| 1–2 | Capa e **glossário** | Ler o aviso (fictício, apartidário). Passar pelas palavras: lacre, custódia, cofre, selo. |
| 3–4 | O que aconteceu, a equipe | Apresentar Miss Pearl, a Profa. Dra. Lucy (orientadora) e a turma 2026. |
| 5–6 | A trilha de um voto, os 5 selos | Perguntar: "se eu der só o resultado final, como vocês conferem?" |
| 7–11 | Anexo 1 — fichas embaralhadas | Slide 8: votar quem vem primeiro. Slide 9: aceitaria ordenar só pelo horário? Slide 10: tocar Bubble e Merge e comparar. |
| 12–14 | Anexo 2 — triagem | Slide 12: fila, pilha e lista desenhadas. Slide 13: voluntário monta a custódia. |
| 15–21 | Anexo 3 — mapa | Slide 16: votar a rota (a mais curta é inválida!). Slide 17: voluntário anda pelo mapa. Slides 18–19: BFS (camadas) × DFS. Slide 20: voltar pelo "de onde vim". |
| 22–24 | Anexo 4 — cofre | Slide 23: palpite em cada lacre. Slide 24: os pares "mesma situação?". |
| 25–27 | Anexo 5 e encerramento | Relatório "consistente"; frase final de Miss Pearl. |

As fichas técnicas (verde) ficam fechadas para a turma e abertas para a banca.
