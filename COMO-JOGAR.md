# Como jogar — Urna Lógica (5 minutos)

**Abrir:** dois cliques em **`jogar_navegador.bat`** — o jogo abre no navegador e tudo é clicável (recomendado). Quem prefere o terminal usa `jogar.bat`. Nenhum dos dois precisa de internet.

**No navegador:** a primeira tela tem só três linhas e o botão **▶ Começar**. Cada fase abre com um cartão **Como jogar em 10 segundos** (o botão **❔ Como jogar** o mostra de novo) e tem a faixa laranja **O que fazer agora**, o botão **💡 Dica**, **Desfazer** e **Recomeçar**. Ao vencer, cai um carimbo com o selo e de 1 a 3 **estrelas**: três estrelas = jogar como o computador (o mínimo de ações que a BFS acha nas Fases 2 e 3; a menor energia do Dijkstra no desafio extra). O progresso fica guardado no navegador. O som do carimbo começa desligado (botão 🔇 no topo).

**Perfis:** na abertura, o jogo pergunta quem está jogando — 🎒 Estudante (pra que serve isso na vida e numa auditoria de verdade), 🔧 Colega avaliador (como validar cada fase em 1 minuto e quais testes comprovam) ou 🎓 Professora (a conexão de cada fase com as aulas e os slides). Dá para trocar no botão 👤 do topo ou ver os três ("Ver tudo").

**Ajuda para quem é leigo:** a Miss Pearl conta o que está acontecendo em cada fase; os botões verdes com ❔ (e o 📖 Dicionário no topo) explicam cada palavra em três camadas — no jogo, na eleição e o conceito da aula; os quadros **Para decidir** explicam as opções antes de cada escolha. Ao ganhar um selo, o carimbo oferece **▶ Ir para a próxima fase**.

**Fase 1 no navegador:** em vez de escolher um critério pronto, monte a chave clicando nas peças **zona → seção → horário**, escolha um método e veja as fichas se moverem.

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
| **Extra (aula 11). Mapa com Custos** | Mesmo mapa, corredores com custos diferentes | Chegar a F gastando o mínimo: 11 de energia | Letra do local · U · R · T tabela · ? dica (Dijkstra) |

**Caminhos que vencem** (para conferir rapidamente):

- Fase 2: `2 1 3 1 4 3 1` (guardar, aceitar, arquivar, aceitar, liberar, arquivar, aceitar)
- Fase 3: `C E C B H D F`
- Fase 4, Sala 1: `1 1 2 1 3 1 4 1 5` · Sala 2: `n s` · `s n` · `s s` · `n s`
- Desafio extra: `B C E C B H D F` (gasta 11; a rota da BFS, `C E C B H D F`, gasta 15)

**Outras opções do menu inicial**

- **2 Resolver:** o computador resolve as Fases 2 e 3 sozinho (BFS ou DFS) e mostra o caminho, os estados explorados e a árvore de busca. A opção 3 compara BFS, guloso e Dijkstra no mapa com custos.
- **4 Resultados:** o que você já fez em cada fase.
- **5 Visualização:** abre no navegador a apresentação animada da investigação.

**Para conferir o código:** `rodar_testes.bat` roda os 151 testes automáticos (deve terminar em `OK`). O código está organizado em `estruturas/` (lista, pilha, fila, AVL, heap, grafo), `algoritmos/` (ordenações, BFS, DFS, solver, Dijkstra), `jogo/` (regras das fases) e `interface/` (telas). Cada função traz no comentário o pseudocódigo da aula correspondente.
