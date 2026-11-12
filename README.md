# Urna Lógica — O Enigma da Eleição de Verídia

Exercício Programa da disciplina Estruturas de Dados e Análise de Algoritmos — Mestrado Profissional em Computação Aplicada, IPT, 2026.

Jogo de lógica e investigação com dados **inteiramente fictícios**. Verídia, seus locais, registros e códigos não correspondem a nenhuma eleição real.

## Requisitos

- Python 3.10 ou superior (testado em 3.14, Windows).
- Nenhuma biblioteca externa e nenhum acesso à internet.

## Como executar

**Jogar (Windows):** dê dois cliques em `jogar.bat`.

**Rodar os testes (Windows):** dê dois cliques em `rodar_testes.bat`.

**Pelo terminal:** abra o `cmd`, entre na pasta do projeto com `cd` e rode:

```
py -m unittest discover -s testes -t .
```

(No Linux/Mac, troque `py` por `python3`.)

Para abrir o jogo pelo terminal: `py jogo.py`.

Situação atual: Fases 1, 2 e 3 jogáveis; solver (BFS, DFS recursiva, DFS com pilha) resolve as Fases 2 e 3; Fases 4 e 5 em construção.

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

- `docs/notas-das-aulas.md` — pseudocódigo das aulas usado como referência.
- `docs/decisoes.md` — escolhas de projeto e pendências.
- `docs/registro-iag.md` — registro de uso de IA generativa (seção 14.4).
