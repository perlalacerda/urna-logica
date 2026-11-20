"""
Gera o RELATÓRIO TÉCNICO (seção 16.1 do enunciado) em HTML e PDF.

    py ferramentas/gerar_relatorio.py

Todas as tabelas de números (métricas, testes, comparações) são calculadas
AGORA, executando o código do jogo: nada é digitado à mão. O PDF é produzido
com o navegador Chromium (Playwright), se estiver instalado; sem ele, fica o HTML,
que pode ser impresso em PDF por qualquer navegador (Ctrl+P → Salvar como PDF).

Saída: docs/relatorio-tecnico.html e docs/relatorio-tecnico.pdf
"""

import html
import io
import os
import platform
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)
sys.setrecursionlimit(10000)

import experimentos                                                     # noqa: E402
from algoritmos.solver import bfs, dfs_recursiva, dfs_pilha              # noqa: E402
from jogo.fase1 import Fase1                                            # noqa: E402
from jogo.fase2 import ProblemaTriagem, EVIDENCIAS                      # noqa: E402
from jogo.fase3 import ProblemaMapa, LOCAIS, ARESTAS, PISTAS, PORTAS, ENERGIA_PADRAO, Fase3   # noqa: E402
from jogo.fase4 import SEQUENCIA_LACRES, PARES_ESTADOS                  # noqa: E402
from jogo.mapa_custos import comparar as comparar_custos, dijkstra_grafo_puro, PESOS, ENERGIA_CUSTOS   # noqa: E402
from ferramentas.gerar_checklist import CAMADAS, linhas_de_codigo       # noqa: E402

DATA = "20.11.2026"
e = html.escape


def tabela(cab, linhas, nota=None, alinhar=None):
    alinhar = alinhar or [""] * len(cab)
    th = "".join(f"<th>{e(c)}</th>" for c in cab)
    tr = "".join("<tr>" + "".join(f'<td class="{a}">{c}</td>' for c, a in zip(l, alinhar)) + "</tr>" for l in linhas)
    return f'<table><tr>{th}</tr>{tr}</table>' + (f'<p class="fonte">{nota}</p>' if nota else "")


def rodar_testes():
    sugestao = unittest.TestLoader().discover("testes", top_level_dir=RAIZ)
    por_arquivo = {}

    def contar(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                contar(t)
            else:
                por_arquivo[t.__class__.__module__] = por_arquivo.get(t.__class__.__module__, 0) + 1
    contar(sugestao)
    r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(sugestao)
    return r.testsRun, len(r.failures) + len(r.errors), por_arquivo


DESCR_TESTES = {
    "testes.test_estruturas": "pilha, fila, lista ligada e AVL (vazias, um elemento, vários, remoção no início/meio/fim, chave duplicada, exemplo da aula 08)",
    "testes.test_ordenacao": "registros, seed, os três métodos em entradas já ordenadas, invertidas, com repetidos; chave composta; estabilidade; Quick do slide",
    "testes.test_fases": "regras da Fase 1 e da Fase 2, jogada inválida sem efeito, desfazer, reiniciar",
    "testes.test_grafo_busca": "grafo, BFS e DFS da aula 09, regras do mapa, solver, integração manual × solver",
    "testes.test_fases_finais": "Fase 4 (rotações, pares de estados, busca), Fase 5 (integração), gerador de mapas",
    "testes.test_dicas": "dicas calculadas pelo solver levam à vitória; entrada por palavras",
    "testes.test_visualizacao": "a visualização usa os dados reais da execução",
    "testes.test_jogo_web": "a página do navegador concorda, jogada a jogada, com as regras em Python",
    "testes.test_mapa_custos": "heap, Dijkstra (exemplo da aula 11), guloso, mapa com custos",
    "testes.test_checklist": "a matriz de inspeção só cita funções e testes que existem",
}


def secoes():
    total, falhas, por_arquivo = rodar_testes()
    ordem = experimentos.medir_ordenacao()
    busca = experimentos.medir_busca()
    avl = experimentos.medir_avl()
    custos = comparar_custos()
    d_puro, _, S_puro, _, cam_puro = dijkstra_grafo_puro()
    f1 = Fase1()
    bfs2 = bfs(ProblemaTriagem())
    P3 = ProblemaMapa()
    r3 = {alg.__name__: alg(P3) for alg in (bfs, dfs_recursiva, dfs_pilha)}
    curto = Fase3().menor_caminho_ignorando_portas()[0]
    ambiente = f"Python {sys.version.split()[0]}, {platform.system()} {platform.release()}, {platform.machine()}"
    S = []

    S.append(("1. Resumo do jogo e objetivo", f"""
<p><b>Urna Lógica — O Enigma da Eleição de Verídia</b> é um jogo de lógica e investigação sobre uma eleição <b>inteiramente fictícia</b>.
A jogadora é analista da Comissão Independente de Verificação (CIV) e precisa recuperar cinco selos de auditoria para abrir o Cofre de Verificação.
Cada fase exercita um conteúdo da disciplina: ordenação de um vetor de registros (Fase 1), fila, pilha e lista ligada (Fase 2),
grafo e busca em largura e em profundidade (Fase 3), árvore AVL como memória de estados (Fase 4) e a integração de tudo numa auditoria final (Fase 5).
Um desafio extra aplica os algoritmos gulosos da aula 11 (Dijkstra com heap próprio).</p>
<p>O jogo tem três modos, todos com as <b>mesmas regras</b>: o <b>manual</b>, em que a jogadora decide; o <b>solver</b>, em que o computador resolve
as Fases 2 e 3 com BFS e DFS; e a <b>visualização</b>, que anima as estruturas com dados reais da execução. A implementação usa Python 3 e só a
biblioteca padrão; o jogo roda no terminal e também no navegador, num único arquivo HTML que funciona sem internet.</p>"""))

    fases = [
        ["1 · Arquivo Embaralhado", "Ordenar 12 registros (seed 2042) pela chave zona → seção → horário", "Bubble, Merge ou Quick; a jogadora monta a chave", "Lote aceito pela auditoria"],
        ["2 · Central de Triagem", "Montar a custódia E2 → E4 → E1 → E6 a partir da fila E1…E6", "Aceitar, guardar (pilha), arquivar, liberar; desfazer", "Custódia completa, fila e pilha vazias"],
        ["3 · Mapa das Seções", f"Ir de A a F com energia {ENERGIA_PADRAO}", "Mover para vizinho; H exige SEQ; F exige AUT", "Chegar a F com AUT"],
        ["4 · Cofre dos Estados", f"Inserir {len(SEQUENCIA_LACRES)} códigos numa AVL; classificar {len(PARES_ESTADOS)} pares de estados", "Prever a rotação; dizer se o estado é repetido", "Sala 1 completa e os pares corretos"],
        ["5 · Auditoria Final", "Refazer as fases 1 a 3 e provar que decorrem das regras", "Escolher o método do relatório", "As três etapas consistentes"],
        ["Extra · Mapa com Custos", f"Mesmo mapa, corredores com custos, energia {ENERGIA_CUSTOS}", "Mover; o custo é w(u, v)", "Chegar a F; ótimo = energia do Dijkstra"],
    ]
    S.append(("2. História, fases, regras e condições de vitória", f"""
<p>Em 2042, uma falha de sincronização embaralhou a apuração simulada de Verídia: os registros ficaram fora de ordem, conexões entre locais
se romperam e parte da trilha de processamento sumiu. A CIV, entidade apartidária, pergunta se é possível reconstruir uma trilha coerente entre
os registros, os locais de votação e o relatório final, respeitando todas as regras. Nenhum nome, partido, número ou resultado de eleição real aparece no jogo.</p>
{tabela(["Fase", "Objetivo", "Ações", "Vitória"], fases)}
<p>Toda jogada inválida é recusada com a explicação do motivo e não altera o estado. Cada fase pode ser reiniciada sem perder os selos das outras.
As regras estão escritas como funções verificáveis (por exemplo, <code>regra_porta</code>, <code>regra_guardar</code>), reutilizadas pelo jogador, pelo solver e pelos testes.</p>"""))

    vert = [[v, e(n), ", ".join(Fase3().G.vizinhos(v)), (f"pista {PISTAS[v]}" if v in PISTAS else "") + (f"porta: exige {PORTAS[v]}" if v in PORTAS else "")] for v, n in LOCAIS.items()]
    S.append(("3. Modelagem dos dados, do grafo e dos estados", f"""
<h3>3.1 Registro e vetor</h3>
<p>Cada registro tem identificador, zona, seção, opção (fictícia), horário e situação. O lote é um vetor de registros gerado por seed e embaralhado
com Fisher–Yates; a mesma seed produz sempre o mesmo lote. A geração sorteia cerca de n/3 horários, para forçar horários repetidos em zonas diferentes:
assim, ordenar só pelo horário não basta. A ordem exigida é uma <b>chave composta</b> (zona, seção, horário), com o identificador como desempate final.</p>
<h3>3.2 Evidências da Fase 2</h3>
<p>Seis evidências chegam numa fila: {", ".join(f"{k} ({e(v)})" for k, v in EVIDENCIAS.items())}. O estado da fase é (fila, pilha, custódia, arquivo).</p>
<h3>3.3 O grafo do mapa</h3>
<p>Grafo não orientado com {len(LOCAIS)} vértices e {len(ARESTAS)} arestas, guardado como <b>lista de adjacência</b>: cada vértice tem uma lista ligada
própria com os vizinhos em ordem alfabética. A escolha segue a aula 09: o mapa é esparso (|E| = {len(ARESTAS)} contra até 36 pares possíveis), e a
lista ocupa O(|V| + |E|), enquanto a matriz ocuparia O(|V|²).</p>
{tabela(["Vértice", "Local", "Vizinhos", "Observação"], vert)}
<h3>3.4 Estado</h3>
<p><b>Estado = (posição, pistas, portas abertas, energia)</b>. Dois estados na mesma posição são diferentes se as pistas forem diferentes: em C sem pistas
e em C com SEQ. O espaço de estados é um <b>grafo implícito</b>: os vizinhos de um estado são gerados pelas regras, não guardados.
Para a memória de visitados, a chave é (posição, pistas, portas) e a energia entra como valor por <b>dominância</b>: um estado repetido com energia menor
ou igual não é expandido; com energia maior, substitui o anterior. Com as mesmas pistas e portas, ter menos energia nunca permite fazer algo novo.</p>
<p>O enigma: ignorando as portas, a BFS acha {" → ".join(curto)} ({len(curto) - 1} arestas), mas essa rota chega a F sem AUT e é recusada.
A rota válida precisa buscar SEQ em E, atravessar H e pegar AUT em D.</p>"""))

    camadas = [[f"<code>{p}/</code>", e(d), str(linhas_de_codigo(p))] for p, d in CAMADAS]
    S.append(("4. Arquitetura do software e divisão dos módulos", f"""
{tabela(["Pasta", "Responsabilidade", "Linhas"], camadas, alinhar=["", "", "num"])}
<p>As dependências vão num único sentido: <code>interface → jogo → algoritmos → estruturas</code>. As estruturas não conhecem o jogo; os algoritmos não
conhecem a tela; as regras ficam em <code>jogo/</code>, uma vez só. O solver recebe um <b>problema</b> com quatro funções (estado inicial, sucessores,
objetivo, chave) e por isso resolve a Fase 2 e a Fase 3 com o mesmo código.</p>
<p>O jogo no navegador não tem uma segunda cópia das regras: <code>interface/jogo_web.py</code> executa as regras em Python, calcula todas as situações
possíveis de cada fase (14 na triagem, 160 no mapa), o resultado de cada jogada e a dica do solver, e grava essas tabelas na página. Um teste refaz cada
jogada das tabelas em Python e confere que o resultado é idêntico. Essa abordagem só vale para espaços de estados pequenos (ver seção 10).</p>"""))

    estr = [
        ["Lista ligada com cabeça", "<code>estruturas/lista_ligada.py</code>", "inserir no início/fim O(1) (ponteiro para o último); buscar e remover O(n)", "custódia; listas de adjacência"],
        ["Pilha dinâmica", "<code>estruturas/pilha.py</code>", "push, pop, peek O(1); pop vazia devolve (False, None)", "pilha de espera; desfazer; DFS com pilha"],
        ["Fila dinâmica", "<code>estruturas/fila.py</code>", "enqueue, dequeue O(1)", "esteira da Fase 2; BFS"],
        ["Árvore AVL", "<code>estruturas/avl.py</code>", "inserir, buscar O(log n); rotações O(1); altura da vazia = −1", "visitados do solver; Fase 4"],
        ["Heap binário de mínimo", "<code>estruturas/heap.py</code>", "inserir, extrair mínimo, diminuir chave O(log n)", "Dijkstra (desafio extra)"],
        ["Grafo", "<code>estruturas/grafo.py</code>", "vizinhos O(grau); pesos w(u, v) ≥ 0", "mapa das Fases 3 e extra"],
    ]
    S.append(("5. Implementação das estruturas de dados", f"""
<p>Todas as estruturas são implementações próprias, sem usar listas ou filas prontas da linguagem como a própria estrutura. Cada função traz, em comentário,
o pseudocódigo do slide correspondente com a numeração das linhas, para conferência lado a lado.</p>
{tabela(["Estrutura", "Arquivo", "Operações e custo", "Uso no jogo"], estr)}
<p>A AVL segue a aula 08: fator de balanceamento FB = altura da esquerda − altura da direita; após a inserção, o ancestral desbalanceado mais próximo é
corrigido com RD, RE, RED ou RDE. A sequência da aula (70, 50, 40, 80, 90, 15, 25, 45, 42) provoca as quatro rotações, e a Fase 4 a usa para que a jogadora
preveja cada uma. O heap segue o heap de máximo da aula 08 com as comparações invertidas, como a aula indica.</p>"""))

    custos_l = [[e(r.algoritmo), "sim" if r.encontrou else "<b>não</b> (trava)", str(r.numero_acoes()), str(r.custo), " → ".join(x[0] for _, x in r.caminho)] for r in custos]
    sol3 = [[e(r.algoritmo), str(r.numero_acoes()), str(r.expandidos), str(r.repetidos), str(r.maior_fronteira), " → ".join(x[0] for _, x in r.caminho)] for r in r3.values()]
    S.append(("6. Implementação e comparação dos algoritmos", f"""
<h3>6.1 Ordenação</h3>
<p>Bubble Sort iterativo e recursivo (aula 02), Merge Sort (aula 02) e Quick Sort com a partição de Lomuto e pivô no último elemento (aula 04). Os três
recebem a mesma chave composta e contam comparações e movimentações. No lote da Fase 1 ({len(f1.registros)} registros), os três chegam à mesma ordem;
o que muda é o trabalho (seção 8).</p>
<p><b>Observação sobre o slide do Quick Sort:</b> com a partição de Lomuto, a chamada recursiva precisa ser <code>quickSort(A, p, q − 1)</code>. Com
<code>quickSort(A, p, q)</code>, como está no slide, a recursão não termina quando o pivô é o maior elemento. O código usa <code>q − 1</code>, e um teste
reproduz o laço infinito da versão literal (<code>test_quick_versao_literal_do_slide_nao_termina</code>).</p>
<h3>6.2 BFS e DFS da aula 09</h3>
<p><code>algoritmos/busca_grafo.py</code> implementa BFS (cores, d, π, fila) e DFS (tempos de descoberta e finalização) literalmente, e os testes usam
os exemplos dos slides. A BFS garante o menor número de <b>arestas</b>; não garante o menor <b>custo</b> quando as arestas têm pesos diferentes (6.4).</p>
<h3>6.3 Solver no espaço de estados</h3>
<p>BFS com a fila própria, DFS recursiva (pilha de chamadas) e DFS com a pilha própria, todas sobre o grafo implícito de estados e com a AVL como memória
de visitados. Cada resultado registra caminho, custo, estados expandidos, gerados e repetidos, fronteira máxima, árvore de busca e métricas da AVL.
Na Fase 2, a BFS acha a custódia em {bfs2.numero_acoes()} ações. Na Fase 3:</p>
{tabela(["Estratégia", "Ações", "Expandidos", "Repetidos barrados", "Fronteira máx.", "Caminho"], sol3, alinhar=["", "num", "num", "num", "num", ""])}
<p>A BFS acha o caminho com menos movimentos, porque cada movimento custa 1. A DFS chega com mais movimentos e não tem essa garantia.
O solver justifica a escolha da BFS para o jogo: a dica precisa ser o caminho mais curto.</p>
<h3>6.4 Algoritmos gulosos (aula 11, desafio extra)</h3>
<p>Mesmo mapa com custos por corredor ({", ".join(f"{u}-{v} = {w}" for (u, v), w in PESOS.items())}) e energia {ENERGIA_CUSTOS}.
O Dijkstra da aula está implementado linha a linha (<code>inicializa</code>, <code>relaxa</code>, <code>dijkstra</code>) e também sobre o grafo de estados;
o guloso ingênuo escolhe sempre o corredor mais barato e nunca volta atrás.</p>
{tabela(["Estratégia", "Chegou", "Movimentos", "Energia", "Rota"], custos_l, alinhar=["", "", "num", "num", ""])}
<p>Menos movimentos não significa menos energia: a BFS pega o atalho A-C (custo 6). O guloso escolhe bem cada passo isolado e mesmo assim trava, como o
troco de 19 com moedas {{2, 3, 6}}. O Dijkstra também é guloso, mas escolhe pelo custo total desde a origem; com pesos não negativos, essa escolha é segura.
No grafo puro, sem portas, o Dijkstra acha {" → ".join(cam_puro)} com custo {d_puro["F"]}, rota que atravessa H sem SEQ: por isso o desafio usa o
Dijkstra sobre o espaço de estados.</p>"""))

    tst = [[f"<code>{m.replace('testes.', '')}.py</code>", str(n), DESCR_TESTES.get(m, "")] for m, n in sorted(por_arquivo.items())]
    S.append(("7. Estratégia e resultados dos testes", f"""
<p>Um arquivo de testes por módulo (biblioteca <code>unittest</code>), cobrindo os casos mínimos da seção 15 do enunciado: estruturas vazias e com um
elemento, remoções nas pontas, entradas já ordenadas e invertidas, chaves duplicadas, destino inalcançável, estados repetidos, regras do jogo e integração.
Os exemplos dos slides viram testes (BFS da aula 09, rotações da aula 08, Dijkstra da aula 11), o que confirma que o código segue a aula.</p>
{tabela(["Arquivo", "Testes", "O que cobre"], tst, alinhar=["", "num", ""])}
<p><b>Resultado: {total} testes, {falhas} falha(s).</b> Para rodar: <code>python -m unittest discover -s testes -t .</code> (ou <code>rodar_testes.bat</code>).</p>
<p>Além dos testes automáticos, cada mudança na interface foi conferida com uma partida completa num navegador automatizado, que clica nas cinco fases e
verifica mensagens, selos e erros de console. Essas partidas revelaram defeitos que os testes de unidade não pegariam (seção 10).</p>"""))

    ord_l = [[str(n), t, e(a), f"{c:,}".replace(",", "."), f"{m:,}".replace(",", "."), f"{ms:.2f}"] for n, t, a, c, m, ms in ordem if n in (100, 1000, 2000)]
    busca_l = [[e(b[0].split(" (")[0] + " (" + b[0].split(" (")[1]), e(b[1]), str(b[2]), str(b[3]), str(b[5]), str(b[6]), str(b[8]), f"{b[10]:.2f}"] for b in busca]
    avl_l = [[str(n), str(h), f"{lg:.2f}", str(r), f"{ms:.2f}"] for n, h, lg, r, ms in avl]
    S.append(("8. Análise de complexidade e desempenho", f"""
<p>Ambiente: {e(ambiente)}. Seed 2042; tempos são a mediana de 5 repetições, em milissegundos. Os tempos dependem da máquina; as contagens não.</p>
<h3>8.1 Ordenação</h3>
{tabela(["n", "entrada", "método", "comparações", "movimentações", "tempo (ms)"], ord_l, "Fonte: experimentos.py, executado na geração deste relatório.", ["num", "", "", "num", "num", "num"])}
<p>O Bubble faz sempre n(n−1)/2 comparações: Θ(n²) (4.950 com n = 100; 499.500 com n = 1.000 — dez vezes mais dados, cem vezes mais comparações).
O Merge fica em Θ(n log n) em todos os casos. O Quick fica em Θ(n log n) com entrada aleatória, mas cai para Θ(n²) com entrada já ordenada ou invertida,
porque o pivô no último elemento divide o vetor em partes de tamanho n − 1 e 0. Com n = 2.000, a entrada ordenada não foi medida no Quick: a recursão
teria profundidade n.</p>
<h3>8.2 Busca no espaço de estados</h3>
{tabela(["cenário", "estratégia", "ações", "expandidos", "repetidos", "fronteira máx.", "altura AVL", "tempo (ms)"], busca_l, "Fonte: experimentos.py; mapas de 30 e 60 vértices gerados por seed.", ["", "", "num", "num", "num", "num", "num", "num"])}
<p>BFS e DFS custam O(|V| + |E|) no grafo de estados, mas esse grafo cresce com as combinações de posição, pistas e portas: com p pistas, até
|V|·2<sup>p</sup> estados. A memória de visitados na AVL custa O(log n) por consulta; sem ela, estados repetidos seriam expandidos de novo.
Nos mapas gerados, a BFS acha sempre o caminho mais curto; a DFS chega com caminhos bem mais longos (35 contra 7 ações no mapa de 30 vértices).</p>
<h3>8.3 Árvore AVL</h3>
{tabela(["nós", "altura", "log₂ n", "rotações", "tempo total de inserção (ms)"], avl_l, "Inserção em ordem crescente, o pior caso de uma árvore de busca comum.", ["num", "num", "num", "num", "num"])}
<p>Inserindo chaves em ordem, uma árvore de busca comum viraria uma lista de altura n − 1. A AVL mantém a altura próxima de log₂ n
(13 com 10.000 nós), por isso busca e inserção custam O(log n).</p>
<h3>8.4 Dijkstra e heap</h3>
<p>Com heap binário, O((|V| + |E|) log |V|): até |V| extrações de mínimo e até |E| relaxamentos, cada um O(log |V|). Com vetor no lugar do heap,
O(|V|²). Inserir e extrair do heap custa O(log n); numa lista não ordenada, extrair o mínimo custaria O(n).</p>"""))

    S.append(("9. Uso de IAG e curadoria humana", """
<p>O código, os testes e a documentação foram produzidos com o apoio do Claude (Anthropic). O registro completo, com o objetivo de cada pedido, o que foi
aproveitado, o que foi alterado e como foi validado, está em <code>docs/registro-iag.md</code> (seção 14.4 do enunciado).</p>
<p>A curadoria humana definiu o que o jogo precisava ser e recusou o que não servia:</p>
<ul>
<li><b>Fidelidade às aulas:</b> o pseudocódigo de cada slide foi transcrito antes do código (transcrição mantida fora do repositório público, por respeito ao material da professora), e cada função foi
conferida contra ele; os exemplos dos slides viraram testes. Essa conferência encontrou a divergência do Quick Sort (6.1).</li>
<li><b>Decisões de projeto</b> registradas com a origem (enunciado, aula ou equipe) em <code>docs/decisoes.md</code>: chave de estado com dominância de energia,
ação "arquivar" na Fase 2, variante com custos sem alterar a Fase 3 original.</li>
<li><b>Jogabilidade:</b> a aluna jogou como avaliadora e apontou o que não estava claro (termos técnicos sem tradução, regras do mapa, falta de botão
"próxima fase", Fase 4 longa); a interface foi revista a partir dessa avaliação.</li>
<li><b>Recusas:</b> pedidos de usar personagens protegidos e dados de seções reais foram substituídos por personagens originais e dados fictícios, como o
enunciado exige; um exemplo narrativo considerado fora de contexto foi retirado.</li>
<li><b>Verificação independente da IA:</b> testes automáticos, partidas completas em navegador automatizado e conferência das afirmações do guia contra
a execução (por exemplo, a afirmação de que Merge e Quick não são estáveis virou teste).</li>
</ul>"""))

    S.append(("10. Dificuldades, limitações, melhorias e conclusão", f"""
<h3>Dificuldades e como foram resolvidas</h3>
<ul>
<li><b>Quick Sort do slide:</b> a chamada <code>p..q</code> não termina com a partição de Lomuto; adotado <code>p..q−1</code>, com teste (pendente de confirmação com a professora).</li>
<li><b>Integração da Fase 5:</b> uma partida simulada revelou que a Fase 5 lia o histórico da Fase 2 num formato diferente do gravado; corrigido e coberto por teste de integração.</li>
<li><b>Conflitos de tecla:</b> no terminal, a tecla de dica "D" coincidia com o local D do mapa; no desafio extra, "C" coincidia com o local C. Trocadas por "?" e "T".</li>
<li><b>Escolha dos custos do desafio extra:</b> os pesos foram escolhidos por busca automática, com o critério de que BFS, guloso e Dijkstra dessem respostas diferentes; uma busca exaustiva confirma que 11 é o mínimo.</li>
</ul>
<h3>Limitações</h3>
<ul>
<li>O jogo no navegador guarda tabelas pré-calculadas de todas as situações; isso só é viável para espaços pequenos (14 e 160 estados). Mapas grandes ficam no solver em Python.</li>
<li>O Quick Sort com pivô fixo degrada para Θ(n²) em entradas ordenadas; não foi implementada escolha aleatória de pivô, para manter o algoritmo da aula.</li>
<li>Os tempos foram medidos em {e(ambiente)}; em outra máquina os valores absolutos mudam, as contagens não.</li>
<li>Kruskal e conjuntos disjuntos (aula 11) não foram implementados; editor de fases, níveis selecionáveis e modo cooperativo (bônus) também não.</li>
</ul>
<h3>Melhorias possíveis</h3>
<ul>
<li>Montar a árvore geradora do gerador de mapas com Kruskal e Union-Find.</li>
<li>A* comparado a BFS e Dijkstra (bônus de heurística).</li>
<li>Programação dinâmica: a memória de visitados já aplica a ideia de não resolver o mesmo subproblema duas vezes; um exemplo explícito (tabela) poderia ser mostrado na Fase 4.</li>
</ul>
<h3>Conclusão</h3>
<p>O jogo cumpre os requisitos obrigatórios com estruturas próprias e algoritmos fiéis às aulas, e mostra, com números medidos, as diferenças que a teoria
prevê: Θ(n²) contra Θ(n log n) na ordenação, menor número de arestas (BFS) contra menor custo (Dijkstra) na busca, altura logarítmica da AVL.
Separar regras, estruturas, algoritmos e telas permitiu que o mesmo código servisse ao jogador, ao solver, aos testes e às duas interfaces.
Resultado dos testes: {total} testes, {falhas} falha(s).</p>"""))
    return S, total, falhas


CSS = """
@page { size: A4; margin: 22mm 18mm 20mm 18mm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 12pt; line-height: 1.45; color: #1b1b1b; }
h1 { font-size: 20pt; margin: 0 0 6pt; } h2 { font-size: 15pt; margin: 22pt 0 8pt; border-bottom: 2px solid #d9682b; padding-bottom: 3pt; page-break-after: avoid; }
h3 { font-size: 12.5pt; margin: 14pt 0 6pt; page-break-after: avoid; }
p, li { text-align: justify; } code { font-family: Consolas, "Courier New", monospace; font-size: 10.5pt; background: #f3eee3; padding: 0 3px; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 4pt; font-size: 10pt; page-break-inside: auto; }
tr { page-break-inside: avoid; } th { background: #2e1d11; color: #fff; text-align: left; padding: 4pt 5pt; font-weight: bold; }
td { border-bottom: 1px solid #d8cdb5; padding: 3pt 5pt; vertical-align: top; } td.num { text-align: right; white-space: nowrap; }
.fonte { font-size: 9pt; color: #555; margin: 0 0 8pt; }
.capa { height: 245mm; display: flex; flex-direction: column; justify-content: center; text-align: center; page-break-after: always; }
.capa .inst { font-size: 13pt; color: #444; } .capa h1 { font-size: 26pt; margin: 30pt 0 8pt; } .capa .sub { font-size: 14pt; margin-bottom: 40pt; }
.sumario li { text-align: left; }
"""


def gerar():
    S, total, falhas = secoes()
    capa = f"""<div class="capa"><div class="inst">IPT — Instituto de Pesquisas Tecnológicas<br>Mestrado Profissional em Computação Aplicada<br>
      Estruturas de Dados e Análise de Algoritmos — 2026</div>
      <h1>Urna Lógica<br>O Enigma da Eleição de Verídia</h1><div class="sub">Relatório técnico do Exercício Programa</div>
      <div>Aluna: Perla Lacerda<br>Professora: Profa. Dra. Lucy Mari Tabuti<br><br>São Paulo, {DATA}</div></div>"""
    sumario = "<h2>Sumário</h2><ol class='sumario'>" + "".join(f"<li>{e(t.split('. ', 1)[1])}</li>" for t, _ in S) + "</ol>"
    corpo = "".join(f"<h2>{e(t)}</h2>{c}" for t, c in S)
    doc = f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>Urna Lógica — Relatório técnico</title><style>{CSS}</style></head><body>{capa}{sumario}{corpo}</body></html>"
    caminho_html = os.path.join(RAIZ, "docs", "relatorio-tecnico.html")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(doc)
    caminho_pdf = os.path.join(RAIZ, "docs", "relatorio-tecnico.pdf")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            pg.goto("file://" + caminho_html.replace(os.sep, "/"))
            pg.pdf(path=caminho_pdf, format="A4", print_background=True, display_header_footer=True,
                   header_template="<span></span>",
                   footer_template='<div style="font-size:9px;width:100%;text-align:center;color:#666">Urna Lógica — Relatório técnico · <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
                   margin={"top": "20mm", "bottom": "18mm", "left": "18mm", "right": "18mm"})
            b.close()
        pdf = True
    except Exception as erro:            # sem Playwright: fica o HTML, que se imprime em PDF pelo navegador
        print("PDF não gerado:", erro)
        pdf = False
    return caminho_html, (caminho_pdf if pdf else None), total, falhas


if __name__ == "__main__":
    h, p, t, f = gerar()
    print(f"HTML: {os.path.relpath(h, RAIZ)}  PDF: {os.path.relpath(p, RAIZ) if p else '—'}  testes: {t}, falhas: {f}")
