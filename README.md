# Urna Lógica — O Enigma da Eleição de Verídia

Exercício Programa da disciplina Estruturas de Dados e Análise de Algoritmos — Mestrado Profissional em Computação Aplicada, IPT, 2026.

Jogo de lógica e investigação com dados **inteiramente fictícios**. Verídia, seus locais, registros e códigos não correspondem a nenhuma eleição real.

**Primeira vez? Leia [COMO-JOGAR.md](COMO-JOGAR.md)** — uma página com as teclas e o caminho de cada fase.

## Requisitos

- Python 3.10 ou superior (testado em 3.14, Windows).
- Nenhuma biblioteca externa e nenhum acesso à internet.

## Como executar

**Jogar (Windows):** dê dois cliques em `jogar.bat`.

**Visualização animada (Windows):** dê dois cliques em `visualizar.bat` (ou opção 5 do menu). Abre `visualizacao.html` no navegador, sem internet.

**Rodar os testes (Windows):** dê dois cliques em `rodar_testes.bat`.

**Pelo terminal:** abra o `cmd`, entre na pasta do projeto com `cd` e rode:

```
py -m unittest discover -s testes -t .
```

(No Linux/Mac, troque `py` por `python3`.)

Para abrir o jogo pelo terminal: `py jogo.py`.

Situação atual: as 5 fases são jogáveis do início ao Cofre de Verificação; o solver (BFS, DFS recursiva, DFS com pilha) resolve as Fases 2 e 3; a Fase 5 valida tudo e grava `resultados/relatorio_auditoria.txt`.

Para gerar as métricas do relatório técnico: `py experimentos.py` (grava `docs/metricas.md`).

## Organização

```
estruturas/   implementações próprias: lista ligada, pilha, fila, AVL, grafo
algoritmos/   Bubble, Merge e Quick Sort; BFS e DFS da aula 09; solver no espaço de estados
jogo/         regras e dados do jogo (registros, fases, mapa)
interface/    telas do terminal (sem regras do jogo)
testes/       um arquivo de testes por módulo (seção 15 do enunciado)
docs/         notas das aulas, decisões de projeto, registro de uso de IAG
```

Cada função traz, em comentário, o pseudocódigo da aula correspondente, com a numeração das linhas. Assim é possível conferir o código lado a lado com o slide.

## Documentos

- `docs/guia-codigo-conceitos.md` — **guia de estudo**: cada conceito da disciplina ligado ao jogo, ao código, à complexidade e ao teste que o comprova (inclui os bônus).
- `docs/roteiro-apresentacao.md` — **roteiro da demonstração** em sala (20 min), com falas, sequência de jogadas e plano B.

- `docs/notas-das-aulas.md` — pseudocódigo das aulas usado como referência.
- `docs/decisoes.md` — escolhas de projeto e pendências.
- `docs/metricas.md` — métricas de ordenação, busca e AVL (gerado por `experimentos.py`).
- `docs/registro-iag.md` — registro de uso de IA generativa (seção 14.4).
