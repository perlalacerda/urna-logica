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

- **Modo aluno 9.º ano (15.11.2026):** a jogabilidade foi revista a partir da avaliação da Perla jogando como a professora (termos sem tradução, Fase 3 sem entender como jogar, Fase 4 longa demais, Fase 5 sem explicar a escolha do método, falta de "próxima fase"). Os termos do jogo ganharam nomes lúdicos (fila de chegada, pilha de espera, lista de custódia, arquivo morto) e cada um leva ao conceito da aula. Os nomes do código (aceitar, guardar, arquivar, liberar) continuam nas regras completas, para a banca ligar tela e código. A tradução do custo usa "1 segundo por comparação" como ilustração, não como medida real. [Equipe]

- **Perfis de quem joga (20.11.2026, pedido da aluna):** em vez de pôr o conteúdo dos três públicos na mesma página só com cores (o que triplicaria o texto), a abertura pergunta o perfil e ele decide qual bloco aparece aberto; cores e ícones dão identidade a cada perfil, e "Ver tudo" mostra os três recolhidos. Os exemplos do cotidiano são analogias didáticas, sem afirmar como cada aplicativo funciona por dentro. [Equipe]
