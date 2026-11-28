# Comece aqui — guia para quem avalia

**Urna Lógica — O Enigma da Eleição de Verídia** · EP de Estruturas de Dados e Análise de Algoritmos · IPT, Mestrado Profissional em Computação Aplicada, 2026.
Linguagem: **Python 3** (só biblioteca padrão). O jogo também roda **no navegador**, num único arquivo HTML que funciona sem internet.

## Em 1 minuto: o que abrir

| Quero… | Abra |
|---|---|
| **Jogar sem instalar nada** | Jogo online: <https://perlalacerda.github.io/urna-logica/> (ou o arquivo `jogo.html`, com dois cliques) |
| **Ver onde cada algoritmo está no código** | [`checklist-entrega.md`](checklist-entrega.md) — conteúdo → aula e slide → arquivo:**linha** → teste |
| **Ler o relatório técnico** | [`relatorio-tecnico.pdf`](relatorio-tecnico.pdf) (estrutura da seção 16.1 do enunciado) |
| **Ver as respostas de cada fase** | [`../COMO-JOGAR.md`](../COMO-JOGAR.md) (contém o gabarito) |
| **Ver o uso de IA** | Declaração na tela **Resultados** do jogo; o registro detalhado (seção 14.4) acompanha a entrega à professora |

## Onde está o essencial

O que a disciplina avalia está em **duas pastas**; o resto é jogo e telas, separados de propósito.

```
estruturas/   lista ligada, pilha, fila, AVL, heap, grafo        ← implementações próprias
algoritmos/   Bubble, Merge, Quick; BFS e DFS da aula 09;       ← o pseudocódigo do slide
              solver no espaço de estados; Dijkstra e guloso       está no comentário, linha a linha
jogo/         regras de cada fase (funções puras, sem tela)
interface/    terminal, jogo no navegador, visualização (sem regras)
testes/       um arquivo de testes por módulo
```

As **regras** do jogo existem uma vez só, em `jogo/`. O jogador, o solver, os testes e a página do navegador usam as mesmas funções. A página não tem regras próprias: o Python calcula as situações possíveis e a página só as consulta (`testes/test_jogo_web.py` confere jogada a jogada).

## Rota de avaliação sugerida (10 minutos)

1. **Testes** — `rodar_testes.bat` (Windows) ou `python -m unittest discover -s testes -t .` → deve terminar em **OK** (151 testes).
2. **Jogar uma fase** — no jogo, **▶ Começar**. A Fase 1 leva cerca de 2 minutos; todas as fases podem ser abertas pelo menu, sem jogar as anteriores.
3. **Solver** — no menu, **Resolver**: BFS, DFS recursiva e DFS com pilha nas Fases 2 e 3, com caminho, estados expandidos, repetidos barrados, fronteira máxima e árvore de busca.
4. **Conferir um algoritmo** — escolha uma linha da [matriz](checklist-entrega.md), clique na função e compare o comentário com o slide citado.

## Critérios de avaliação (seção 17 do enunciado) — onde conferir

Os critérios e os pesos são os do enunciado. A coluna "Onde conferir" aponta a evidência neste projeto.

| Critério | Peso | Onde conferir |
|---|---|---|
| Corretude funcional e jogabilidade | 20 | Jogo no navegador: **▶ Começar**, 💡 Dica, Desfazer, Recomeçar e Zerar progresso; toda jogada inválida é recusada com o motivo; tela final com o Cofre de Verificação. Testes: `testes/test_jogo_web.py`, `testes/test_fases.py` |
| Estruturas de dados | 20 | `estruturas/` (lista ligada com nó cabeça, pilha, fila); registros em vetor em `jogo/registros.py` (Fase 1); fila, pilha e lista de custódia na Fase 2 (`jogo/fase2.py`). Testes: `testes/test_estruturas.py` |
| Algoritmos | 20 | `algoritmos/ordenacao.py` (Bubble, Merge, Quick), `algoritmos/busca_grafo.py` (BFS e DFS da aula), `algoritmos/solver.py` (BFS, DFS recursiva e DFS com pilha, com as mesmas regras do jogador). Comparações em `docs/metricas.md`. Testes: `testes/test_ordenacao.py`, `testes/test_grafo_busca.py` |
| Grafo, estados e AVL | 20 | `estruturas/grafo.py` (lista de adjacência); estado e chave em `jogo/fase3.py` (`chave_estado` inclui a energia, enunciado 8.1); `estruturas/avl.py` com as quatro rotações; Fase 4 (`jogo/fase4.py`); relatório, seção 5.1. Testes: `test_chave_inclui_energia`, `test_estados_repetidos_nao_sao_expandidos` |
| Testes e análise técnica | 15 | 151 testes com casos-limite e integração jogador × solver; `experimentos.py` mede e grava `docs/metricas.md`; complexidade no relatório (seção 8) |
| Criatividade, narrativa e experiência | 15 | Cada fase é um elo da auditoria de Verídia, narrado pela Miss Pearl, com quadro "O que aprendemos" e o "depende"; três perfis (estudante, colega, professora); Audiência Pública (`visualizacao.html`) |
| Relatório e curadoria de IAG | 10 | `docs/relatorio-tecnico.pdf`; decisões marcadas [EP] ou [Equipe] em `docs/decisoes.md`; registro de uso de IA (seção 14.4) acompanha a entrega |
| Bônus (seção 18) | +30 | Mapas gerados por seed com verificação de solução (`jogo/cenarios.py`); visualização animada (`visualizacao.html`); heap de mínimo próprio usado no Dijkstra do desafio extra (`estruturas/heap.py`, `algoritmos/dijkstra.py`); piloto da Fase 3 em Phaser (`phaser/`) |

## Como executar (três formas)

| Forma | Como |
|---|---|
| Navegador, online | Link acima. Nada para instalar. |
| Navegador, sem internet | Dois cliques em `jogo.html` (ou `jogar_navegador.bat`). |
| Terminal | `python jogo.py` (ou `jogar.bat`). Python 3.10 ou superior. |



## Documentos

| Documento | Conteúdo |
|---|---|
| [`checklist-entrega.md`](checklist-entrega.md) | Matriz de inspeção (gerada pelo código) |
| [`relatorio-tecnico.pdf`](relatorio-tecnico.pdf) | Relatório técnico (seção 16.1) |
| [`guia-codigo-conceitos.md`](guia-codigo-conceitos.md) | Guia de estudo: cada conceito, o código, a complexidade e o teste |
| [`decisoes.md`](decisoes.md) | Decisões de projeto e pendências |
| [`metricas.md`](metricas.md) | Métricas medidas (gerado por `experimentos.py`) |
| [`roteiro-apresentacao.md`](roteiro-apresentacao.md) | Roteiro da demonstração em sala |
| [`prints/`](prints/) | Telas do jogo |
