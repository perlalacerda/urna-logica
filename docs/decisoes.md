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

## Regras das fases (em definição)

- **Fase 2:** o enigma E2 → E4 → E1 → E6 exige destino para E3 e E5. Proposta: ação **arquivar** (evidência fora da custódia). Pendente de aprovação.
- **Fase 3:** o enunciado chama E de "Unidade Oeste" (7.1) e "Arquivo Oeste" (7.5); a porta que exige a pista de sequência fica em outro local no mapa final. Pendente.

## Pendências com a professora

1. Quick Sort: `p..q` do slide × `p..q-1`.
2. Fase 2: ação "arquivar".
3. Fase 3: nome e regra da porta do Oeste.
4. Bônus "editor de fases": fases em arquivo JSON contam?
