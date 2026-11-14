# Como jogar — Urna Lógica (5 minutos)

**Abrir:** dois cliques em **`jogar_navegador.bat`** — o jogo abre no navegador e tudo é clicável (recomendado). Quem prefere o terminal usa `jogar.bat`. Nenhum dos dois precisa de internet.

**No navegador:** cada fase tem a faixa laranja **O que fazer agora**, o botão **💡 Dica**, **Desfazer** e **Recomeçar**. O progresso fica guardado no navegador.

**No terminal:** digite o número (ou a palavra) da opção e tecle **Enter**.
Em toda fase aparece a linha **>> O QUE FAZER AGORA**. Se travar, digite **?** (ou a palavra *dica*) para receber uma dica.
Nada quebra o jogo: uma jogada errada é recusada com explicação e não muda nada.

**Objetivo:** ganhar os 5 selos. No menu inicial, escolha **1 (Jogar)** e depois a fase.

| Fase | O que você faz | Como vencer | Teclas |
|---|---|---|---|
| **1. Arquivo Embaralhado** | Ordena 12 registros fictícios | Opção 2 → qualquer algoritmo → critério **4** (zona, seção, horário) | 1 enigma · 2 ordenar · 3 comparar · ? dica |
| **2. Central de Triagem** | Move evidências da fila para a custódia | Montar **E2 → E4 → E1 → E6** | 1 aceitar · 2 guardar · 3 arquivar · 4 liberar · 5 desfazer · ? dica |
| **3. Mapa das Seções** | Anda pelo mapa até o Centro de Validação (F) | Pegar a pista **SEQ em E** e a pista **AUT em D** antes de entrar em F | Letra do local · U desfazer · R reiniciar · ? dica |
| **4. Cofre dos Estados** | Guarda códigos numa árvore AVL | Sala 1: inserir os 9 lacres · Sala 2: acertar os 4 pares | 1–5 palpite de rotação · s/n · ? dica |
| **5. Auditoria Final** | O sistema confere tudo | Escolher um algoritmo e ler o relatório | 1–3 |

**Caminhos que vencem** (para conferir rapidamente):

- Fase 2: `2 1 3 1 4 3 1` (guardar, aceitar, arquivar, aceitar, liberar, arquivar, aceitar)
- Fase 3: `C E C B H D F`
- Fase 4, Sala 1: `1 1 2 1 3 1 4 1 5` · Sala 2: `n s` · `s n` · `s s` · `n s`

**Outras opções do menu inicial**

- **2 Resolver:** o computador resolve as Fases 2 e 3 sozinho (BFS ou DFS) e mostra o caminho, os estados explorados e a árvore de busca.
- **4 Resultados:** o que você já fez em cada fase.
- **5 Visualização:** abre no navegador a apresentação animada da investigação.

**Para conferir o código:** `rodar_testes.bat` roda os 111 testes automáticos (deve terminar em `OK`). O código está organizado em `estruturas/` (lista, pilha, fila, AVL, grafo), `algoritmos/` (ordenações, BFS, DFS, solver), `jogo/` (regras das fases) e `interface/` (telas). Cada função traz no comentário o pseudocódigo da aula correspondente.
