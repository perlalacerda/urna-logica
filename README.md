# Urna Lógica — O Enigma da Eleição de Verídia

Exercício Programa da disciplina Estruturas de Dados e Análise de Algoritmos — Mestrado Profissional em Computação Aplicada, IPT, 2026.

Jogo de lógica e investigação com dados **inteiramente fictícios**. Verídia, seus locais, registros e códigos não correspondem a nenhuma eleição real.

**Jogar online, sem instalar nada:** <https://perlalacerda.github.io/urna-logica/>

**Vai avaliar? Comece por [docs/COMECE-AQUI.md](docs/COMECE-AQUI.md)** — rota de 10 minutos, [matriz de inspeção](docs/checklist-entrega.md) (conteúdo → aula → arquivo:linha → teste) e [relatório técnico em PDF](docs/relatorio-tecnico.pdf).

**Primeira vez jogando? Leia [COMO-JOGAR.md](COMO-JOGAR.md)** — uma página com as teclas e o caminho de cada fase.

## Requisitos

- Python 3.10 ou superior (testado em 3.14, Windows).
- Nenhuma biblioteca externa e nenhum acesso à internet.

## Como executar

**Jogar no navegador (recomendado):** dê dois cliques em `jogar_navegador.bat`. Tudo é clicável e funciona sem internet. A página é gerada por `interface/jogo_web.py`: o Python calcula, com as regras reais do jogo, todas as situações de cada fase e o resultado de cada jogada; a página só consulta essas tabelas (`testes/test_jogo_web.py` confere).

**Jogar no terminal:** dê dois cliques em `jogar.bat`.

**Visualização animada (Windows):** dê dois cliques em `visualizar.bat` (ou opção 5 do menu). Abre `visualizacao.html` no navegador, sem internet.

**Rodar os testes (Windows):** dê dois cliques em `rodar_testes.bat`.

**Pelo terminal:** abra o `cmd`, entre na pasta do projeto com `cd` e rode:

```
py -m unittest discover -s testes -t .
```

(No Linux/Mac, troque `py` por `python3`.)

Para abrir o jogo pelo terminal: `py jogo.py`.

Situação atual: as 5 fases são jogáveis do início ao Cofre de Verificação; o solver (BFS, DFS recursiva, DFS com pilha) resolve as Fases 2 e 3; a Fase 5 valida tudo e grava `resultados/relatorio_auditoria.txt`.

**Desafio extra (aula 11 — algoritmos gulosos):** o mapa da Fase 3 com corredores de custos diferentes. Compara BFS (menos movimentos), um guloso ingênuo (corredor mais barato, que trava) e o Dijkstra com heap próprio (menor energia). Ver `jogo/mapa_custos.py` e a seção B3 do guia.

Para gerar as métricas do relatório técnico: `py experimentos.py` (grava `docs/metricas.md`).

## Organização

```
estruturas/   implementações próprias: lista ligada, pilha, fila, AVL, heap de mínimo, grafo com pesos
algoritmos/   Bubble, Merge e Quick Sort; BFS e DFS da aula 09; solver no espaço de estados;
              Dijkstra e guloso ingênuo da aula 11
jogo/         regras e dados do jogo (registros, fases, mapa)
interface/    telas do terminal (sem regras do jogo)
testes/       um arquivo de testes por módulo (seção 15 do enunciado)
ferramentas/  geradores da matriz de inspeção, do relatório técnico e dos prints
docs/         notas das aulas, decisões de projeto, registro de uso de IAG
```

Cada função traz, em comentário, o pseudocódigo da aula correspondente, com a numeração das linhas. Assim é possível conferir o código lado a lado com o slide.

## Documentos

- `docs/COMECE-AQUI.md` — **guia para quem avalia** (rota de 10 minutos, onde está o essencial, perguntas prováveis).
- `docs/checklist-entrega.md` — **matriz de inspeção**, gerada pelo código: `py ferramentas/gerar_checklist.py`.
- `docs/relatorio-tecnico.pdf` — **relatório técnico** (seção 16.1), com métricas medidas na geração: `py ferramentas/gerar_relatorio.py`.
- `docs/prints/` — telas do jogo: `py ferramentas/gerar_prints.py`.

- `docs/guia-codigo-conceitos.md` — **guia de estudo**: cada conceito da disciplina ligado ao jogo, ao código, à complexidade e ao teste que o comprova (inclui os bônus).
- `docs/roteiro-apresentacao.md` — **roteiro da demonstração** em sala (20 min), com falas, sequência de jogadas e plano B.

- `docs/decisoes.md` — escolhas de projeto e pendências.
- `docs/metricas.md` — métricas de ordenação, busca e AVL (gerado por `experimentos.py`).
- `docs/registro-iag.md` — registro de uso de IA generativa (seção 14.4).
