"""
Interface em terminal (texto). Só exibe e lê opções: NENHUMA regra do jogo
fica aqui. As regras moram em jogo/ (separação exigida na seção 12).
"""

import textwrap

from jogo import narrativa
from jogo.fase1 import Fase1
from jogo.fase2 import Fase2, EVIDENCIAS, proximo_esperado, ProblemaTriagem, rotulo_triagem
from jogo.fase3 import Fase3, ProblemaMapa, LOCAIS, PISTAS, PORTAS, NOMES_PISTAS, rotulo as rotulo_mapa
from algoritmos.solver import bfs, dfs_recursiva, dfs_pilha, desenhar_arvore_de_busca
from jogo.fase4 import Fase4, OPCOES_ROTACAO, descrever_par
from jogo.fase5 import Fase5
from jogo.registros import DESCRICAO_CRITERIOS

LINHA = "=" * 70


# ------------------------------------------------------------ utilidades
def titulo(texto):
    print("\n" + LINHA)
    print("  " + texto)
    print(LINHA)


def ler_opcao(validas, mensagem="Escolha uma opção: "):
    """Lê até receber uma das opções válidas. Nunca quebra com entrada inválida."""
    while True:
        try:
            valor = input(mensagem).strip().lower()
        except EOFError:
            return "0"
        if valor in validas:
            return valor
        print(f"  Opção inválida. Digite uma destas: {', '.join(validas)}")


def pausa():
    try:
        input("\n(tecle Enter para continuar)")
    except EOFError:
        pass


# ------------------------------------------------------------ o jogo
class JogoTerminal:
    def __init__(self, seed=2042):
        self.seed = seed
        self.fase1 = Fase1(seed=seed)
        self.fase2 = Fase2()
        self.fase3 = Fase3()
        self.fase4 = Fase4()
        self.fase5 = Fase5()

    def selos(self):
        return [self.fase1.selo, self.fase2.venceu(), self.fase3.venceu(),
                self.fase4.venceu(), self.fase5.venceu()]

    def barra_de_selos(self):
        return "  ".join(f"[{'X' if s else ' '}] Selo {i}" for i, s in enumerate(self.selos(), 1))

    # ======================================================== menu inicial
    def executar(self):
        titulo(narrativa.TITULO.upper())
        for paragrafo in narrativa.PROLOGO:
            print(textwrap.fill(paragrafo, 68, initial_indent="  ", subsequent_indent="  ") + "\n")
        print(textwrap.fill("(" + narrativa.AVISO + ")", 68, initial_indent="  ", subsequent_indent="  "))
        while True:
            titulo("MENU INICIAL")
            print("  " + self.barra_de_selos())
            print("\n  1. Jogar\n  2. Resolver (solver automático)\n  3. Instruções\n  4. Resultados"
                  "\n  5. Visualização animada (abre no navegador)\n  0. Sair")
            op = ler_opcao(["1", "2", "3", "4", "5", "0"])
            if op == "1":
                self.menu_jogar()
            elif op == "2":
                self.menu_resolver()
            elif op == "3":
                self.instrucoes()
            elif op == "4":
                self.resultados()
            elif op == "5":
                self.abrir_visualizacao()
            else:
                print("\nAté a próxima auditoria!")
                return

    def menu_jogar(self):
        while True:
            titulo("ESCOLHA A FASE")
            print("  1. " + Fase1.NOME + ("  (selo obtido)" if self.fase1.selo else ""))
            print("  2. " + Fase2.NOME + ("  (selo obtido)" if self.fase2.venceu() else ""))
            print("  3. " + Fase3.NOME + ("  (selo obtido)" if self.fase3.venceu() else ""))
            print("  4. " + Fase4.NOME + ("  (selo obtido)" if self.fase4.venceu() else ""))
            print("  5. " + Fase5.NOME + ("  (selo obtido)" if self.fase5.venceu() else ""))
            print("  0. Voltar")
            op = ler_opcao(["1", "2", "3", "4", "5", "0"])
            if op == "1":
                self.jogar_fase1()
            elif op == "2":
                self.jogar_fase2()
            elif op == "3":
                self.jogar_fase3()
            elif op == "4":
                self.jogar_fase4()
            elif op == "5":
                self.jogar_fase5()
            else:
                return

    def menu_resolver(self):
        while True:
            titulo("SOLVER — busca automática no espaço de estados")
            print("  O solver usa AS MESMAS REGRAS do jogador. Cada situação do jogo é um")
            print("  vértice; cada ação válida é uma aresta. A AVL guarda os estados já vistos.")
            print("\n  Qual desafio?\n  1. Fase 2 — sequência de custódia\n  2. Fase 3 — rota no mapa\n  0. Voltar")
            op = ler_opcao(["1", "2", "0"])
            if op == "0":
                return
            problema, rotulo = ((ProblemaTriagem(), rotulo_triagem) if op == "1"
                                else (ProblemaMapa(), rotulo_mapa))
            print("\n  Estratégia:\n  1. BFS (fila)\n  2. DFS recursiva\n  3. DFS com pilha\n  4. Comparar as três")
            est = ler_opcao(["1", "2", "3", "4"])
            algs = {"1": [bfs], "2": [dfs_recursiva], "3": [dfs_pilha], "4": [bfs, dfs_recursiva, dfs_pilha]}[est]
            resultados = [alg(problema) for alg in algs]
            for r in resultados:
                self.mostrar_resultado(r, rotulo, detalhar=len(algs) == 1)
            if len(resultados) > 1:
                self.tabela_comparativa(resultados)
            pausa()

    def mostrar_resultado(self, r, rotulo, detalhar=True):
        print(f"\n  === {r.algoritmo} ===")
        if r.encontrou:
            print(f"  Solução com {r.numero_acoes()} ações (custo {r.custo}):")
            for i, (acao, e) in enumerate(r.caminho):
                print(f"    {i:>2}. {acao or 'início':12}  {rotulo(e)}")
        else:
            print("  Nenhuma solução: todos os estados alcançáveis foram explorados.")
        print(f"  Estados expandidos: {r.expandidos} | gerados: {r.gerados} | "
              f"repetidos ignorados (AVL): {r.repetidos}")
        print(f"  Fronteira máxima: {r.maior_fronteira} | AVL: {r.avl_nos} nós, altura {r.avl_altura}, "
              f"{r.avl_rotacoes} rotações | tempo: {r.tempo_ms:.3f} ms")
        if detalhar:
            print("\n  Árvore de busca (cada nó é um estado; cada aresta, a ação que levou a ele):")
            print("  " + desenhar_arvore_de_busca(r, rotulo, limite=40).replace("\n", "\n  "))

    def tabela_comparativa(self, resultados):
        print(f"\n  {'estratégia':17} {'ações':>5} {'expandidos':>10} {'gerados':>8} {'repetidos':>9} "
              f"{'fronteira':>9} {'tempo(ms)':>9}")
        for r in resultados:
            print(f"  {r.algoritmo:17} {r.numero_acoes() if r.encontrou else '-':>5} {r.expandidos:>10} "
                  f"{r.gerados:>8} {r.repetidos:>9} {r.maior_fronteira:>9} {r.tempo_ms:>9.3f}")
        print("\n  BFS garante o menor número de ações (cada ação custa 1);")
        print("  DFS pode achar um caminho mais longo, explorando em profundidade.")

    # ======================================================== FASE 1
    def mostrar_lote(self):
        print(f"\n  {'#':>2}  {'id':8} {'zona':>4} {'seção':>5} {'opção':>5}  {'horário':8}  status")
        for i, r in enumerate(self.fase1.registros):
            print(f"  {i:>2}  {r.id_registro:8} {r.zona:>4} {r.secao:>5} {r.opcao:>5}  {r.timestamp:8}  {r.status}")

    def jogar_fase1(self):
        f = self.fase1
        titulo(f.NOME)
        print(f.ABERTURA)
        while True:
            self.mostrar_lote()
            print("\n  1. Ver o enigma\n  2. Ordenar o lote\n  3. Comparar os 3 algoritmos (10, 100, 500 registros)"
                  "\n  4. Reiniciar a fase\n  0. Voltar")
            op = ler_opcao(["1", "2", "3", "4", "0"])
            if op == "1":
                print("\n" + f.ENIGMA)
                pausa()
            elif op == "2":
                print("\n  Algoritmo:  1. Bubble Sort   2. Merge Sort   3. Quick Sort")
                alg = {"1": "bubble", "2": "merge", "3": "quick"}[ler_opcao(["1", "2", "3"])]
                criterios = ["id", "zona", "horario", "auditoria"]
                print("\n  Critério de ordenação:")
                for i, c in enumerate(criterios, 1):
                    print(f"   {i}. {DESCRICAO_CRITERIOS[c]}")
                crit = criterios[int(ler_opcao(["1", "2", "3", "4"])) - 1]
                res = f.ordenar(alg, crit)
                self.mostrar_lote()
                c = res["contador"]
                print(f"\n  {c.algoritmo}: {c.comparacoes} comparações, {c.movimentacoes} movimentações.")
                print("  " + res["mensagem"].replace("\n", "\n  "))
                pausa()
                if f.selo:
                    return
            elif op == "3":
                print(f"\n  {'n':>5}  {'algoritmo':12} {'comparações':>12} {'movimentações':>14} {'tempo (ms)':>11}")
                for n, nome, comp, mov, ms in f.comparar_algoritmos():
                    print(f"  {n:>5}  {nome:12} {comp:>12} {mov:>14} {ms:>11.3f}")
                print("\n  Note: Bubble cresce com n² (n(n-1)/2 comparações); Merge e Quick com n log n.")
                pausa()
            elif op == "4":
                f.reiniciar()
                print("  Fase reiniciada (mesmo lote, mesma seed).")
            else:
                return

    # ======================================================== FASE 2
    def mostrar_triagem(self):
        f = self.fase2
        custodia = f.custodia.percorrer()
        print(f"\n  FILA de entrada   : {f.fila}")
        print(f"  PILHA de espera   : {f.pilha}")
        print(f"  CUSTÓDIA (lista)  : {f.custodia}")
        print(f"  ARQUIVO           : {', '.join(f.arquivo) if f.arquivo else '(vazio)'}")
        esperado = proximo_esperado(custodia, f.alvo)
        print(f"  Objetivo          : {' -> '.join(f.alvo)}"
              + (f"   (próxima esperada: {esperado})" if esperado else ""))

    def regras_fase2(self):
        print("\n  REGRAS DA CENTRAL DE TRIAGEM")
        print("  1 aceitar  : a 1ª da fila entra na custódia, se for a próxima esperada.")
        print("  2 guardar  : a 1ª da fila vai para o topo da pilha, se fizer parte da")
        print("               custódia e precisar sair ANTES de quem está no topo.")
        print("  3 arquivar : a 1ª da fila vai para o arquivo, se NÃO fizer parte da custódia.")
        print("  4 liberar  : o topo da pilha entra na custódia, se for a próxima esperada.")
        print("  5 desfazer : volta à situação anterior à última ação (pilha do histórico).")
        print("\n  Evidências:")
        for e, desc in EVIDENCIAS.items():
            print(f"    {e}: {desc}")

    def jogar_fase2(self):
        f = self.fase2
        titulo(f.NOME)
        print(f.ABERTURA)
        self.regras_fase2()
        mapa = {"1": "aceitar", "2": "guardar", "3": "arquivar", "4": "liberar"}
        while True:
            self.mostrar_triagem()
            if f.venceu():
                print("\n  Selo 2 conquistado! A trilha de evidências está organizada.")
                pausa()
                return
            print("\n  1. aceitar  2. guardar  3. arquivar  4. liberar  5. desfazer"
                  "\n  6. reiniciar a fase  7. ver regras  0. voltar")
            op = ler_opcao(["1", "2", "3", "4", "5", "6", "7", "0"])
            if op in mapa:
                ok, msg = f.executar(mapa[op])
                print("\n  " + ("OK: " if ok else "") + msg.replace("\n", "\n  "))
            elif op == "5":
                print("\n  " + f.desfazer()[1])
            elif op == "6":
                f.reiniciar()
                print("\n  Fase reiniciada.")
            elif op == "7":
                self.regras_fase2()
            else:
                return

    # ======================================================== FASE 3
    def mostrar_mapa(self):
        f = self.fase3
        pos, pistas, portas, energia = f.estado
        print("\n  MAPA (lista de adjacência)")
        for v in f.G.vertices():
            extra = []
            if v in PISTAS:
                extra.append(f"pista {PISTAS[v]}")
            if v in PORTAS:
                extra.append(f"porta: exige {PORTAS[v]}")
            marca = " <== VOCÊ" if v == pos else ""
            print(f"   {v} {LOCAIS[v]:22} -> {', '.join(f.G.vizinhos(v)):12}"
                  f"{('  [' + '; '.join(extra) + ']') if extra else ''}{marca}")
        print(f"\n  Posição: {pos} ({LOCAIS[pos]})   Energia: {energia}   "
              f"Pistas: {', '.join(pistas) or 'nenhuma'}   Portas liberadas: {', '.join(portas) or 'nenhuma'}")
        print(f"  Trilha: {' -> '.join(f.trilha)}")

    def regras_fase3(self):
        print("\n  REGRAS DO MAPA")
        print("  R1 Só é possível ir para um local vizinho (ligado por corredor).")
        print("  R2 Cada movimento gasta 1 de energia. Com energia 0 não se move.")
        print("  R3 O Arquivo Oeste (H) só abre para quem tem a pista de sequência (SEQ).")
        print("  R4 O Centro de Validação (F) só abre para quem tem a pista de autenticação (AUT).")
        print("  R5 Ao chegar na Unidade Oeste (E) você ganha SEQ; na Unidade Leste (D), AUT.")
        print("  Objetivo: chegar ao Centro de Validação (F).")

    def jogar_fase3(self):
        f = self.fase3
        titulo(f.NOME)
        print(f.ABERTURA)
        self.regras_fase3()
        while True:
            self.mostrar_mapa()
            if f.venceu():
                print("\n  Selo 3 conquistado! Caminho de auditoria reconstruído.")
                pausa()
                return
            vizinhos = f.G.vizinhos(f.estado[0])
            print(f"\n  Digite a letra do destino ({', '.join(vizinhos)}), ou:")
            print("  U = desfazer   R = reiniciar   P = ver regras   M = menor caminho ignorando as portas   0 = voltar")
            op = ler_opcao([v.lower() for v in f.G.vertices()] + ["u", "r", "p", "m", "0"],
                           "Sua jogada: ")
            if op == "0":
                return
            if op == "u":
                print("\n  " + f.desfazer()[1])
            elif op == "r":
                f.reiniciar()
                print("\n  Fase reiniciada.")
            elif op == "p":
                self.regras_fase3()
            elif op == "m":
                cam, ordem = f.menor_caminho_ignorando_portas()
                print(f"\n  BFS no grafo puro (aula 09), a partir de A: ordem de visita {' '.join(ordem)}")
                print(f"  Menor caminho em número de arestas: {' -> '.join(cam)} ({len(cam) - 1} arestas)")
                print("  Atenção: ele ignora as portas. Será que é válido pelas regras?")
            else:
                ok, msg = f.ir_para(op)
                print("\n  " + ("OK: " if ok else "") + msg.replace("\n", "\n  "))

    # ======================================================== FASE 4
    def jogar_fase4(self):
        f = self.fase4
        titulo(f.NOME)
        print(f.ABERTURA)
        while True:
            sala1 = f"{f.proximo}/{len(f.sequencia)} lacres" + (" (completa)" if f.sala1_completa() else "")
            sala2 = f"{sum(f.respostas_sala2.values())}/{len(f.pares)} corretas" + (" (completa)" if f.sala2_completa() else "")
            print(f"\n  1. Sala 1 — Lacres do cofre (AVL e rotações)   [{sala1}]")
            print(f"  2. Sala 2 — O estado que parece igual         [{sala2}]")
            print("  3. Sala 3 — Consulta ao cofre (busca)")
            print("  4. Reiniciar a fase\n  0. Voltar")
            op = ler_opcao(["1", "2", "3", "4", "0"])
            if op == "1":
                self.sala1()
            elif op == "2":
                self.sala2()
            elif op == "3":
                self.sala3()
            elif op == "4":
                f.reiniciar()
                print("  Fase reiniciada.")
            else:
                return
            if f.venceu():
                print("\n  O cofre reconheceu a memória organizada. Selo 4 conquistado!")
                pausa()
                return

    def sala1(self):
        f = self.fase4
        print("\n  O cofre indexa os códigos dos lacres numa árvore AVL.")
        print("  Lembre: FB = altura da esquerda - altura da direita; deve ficar entre -1 e +1.")
        print("  Se um nó chegar a +2 ou -2, uma rotação corrige:")
        print("    +2 e entrou à esquerda da esquerda -> RD    -2 e à direita da direita -> RE")
        print("    +2 e entrou à direita da esquerda  -> RED   -2 e à esquerda da direita -> RDE")
        while not f.sala1_completa():
            codigo = f.sequencia[f.proximo]
            print("\n  Árvore atual:")
            print("  " + f.avl.desenhar().replace("\n", "\n  "))
            print(f"\n  Próximo lacre: {codigo}. O que vai acontecer ao inseri-lo?")
            for i, o in enumerate(OPCOES_ROTACAO, 1):
                print(f"   {i}. {o}")
            print("   0. sair da sala (o progresso fica guardado)")
            op = ler_opcao(["1", "2", "3", "4", "5", "0"])
            if op == "0":
                return
            r = f.inserir_proximo(OPCOES_ROTACAO[int(op) - 1])
            print(f"\n  Inserido {r['codigo']}. " + ("Previsão CORRETA!" if r["acertou"] else
                  f"Previsão incorreta: ocorreu '{r['ocorrido']}'."))
            print("  Por quê? " + r["explicacao"])
            if r["ocorrido"] != "nenhuma":
                print("\n  ANTES da inserção:\n  " + r["antes"].replace("\n", "\n  "))
            print("\n  DEPOIS:\n  " + r["depois"].replace("\n", "\n  "))
            print(f"  Altura da árvore: {r['altura']}   Continua AVL? {'sim' if r['eh_avl'] else 'NÃO'}")
            pausa()
        print(f"\n  Sala 1 completa: {f.acertos_sala1()} de {len(f.sequencia)} previsões corretas.")
        rot = f.avl.rotacoes
        print(f"  Rotações realizadas: RD={rot['RD']}, RE={rot['RE']}, RED={rot['RED']}, RDE={rot['RDE']}.")

    def sala2(self):
        f = self.fase4
        print("\n  O solver guarda na AVL a CHAVE de cada estado: (posição, pistas, portas).")
        print("  A energia não entra na chave: fica guardada junto, como valor.")
        for i, par in enumerate(f.pares):
            if f.respostas_sala2.get(i):
                continue
            print(f"\n  Par {i + 1}:\n  {descrever_par(par)}")
            print("  a) Os dois devem ter a MESMA chave na AVL?  (s/n)")
            mesma = ler_opcao(["s", "n"], "  Resposta: ") == "s"
            print("  b) O solver deve EXPLORAR o estado novo?    (s/n)")
            explorar = ler_opcao(["s", "n"], "  Resposta: ") == "s"
            ok, explicacao, _ = f.responder_par(i, mesma, explorar)
            print("  " + ("CORRETO. " if ok else "Não é isso. ") + explicacao)
        if f.sala2_completa():
            print("\n  Sala 2 completa.")
        else:
            print("\n  Há pares a rever. Entre de novo na Sala 2 para tentar outra vez.")
        pausa()

    def sala3(self):
        f = self.fase4
        if f.avl.raiz is None:
            print("\n  O cofre está vazio: insira lacres na Sala 1 primeiro.")
            return
        print("\n  Árvore do cofre:\n  " + f.avl.desenhar().replace("\n", "\n  "))
        try:
            texto = input("\n  Código a procurar (número): ").strip()
            codigo = int(texto)
        except (ValueError, EOFError):
            print("  Digite apenas números.")
            return
        achou, caminho, comps = f.consultar(codigo)
        print(f"  Caminho na árvore: {' -> '.join(map(str, caminho)) or '(vazio)'}")
        print(f"  {'ENCONTRADO' if achou else 'NÃO encontrado'} após {comps} comparações "
              f"(altura da árvore: {f.avl.altura()}; no máximo altura + 1 comparações).")

    # ======================================================== FASE 5
    def jogar_fase5(self):
        f = self.fase5
        titulo(f.NOME)
        print(f.ABERTURA)
        print("\n  Etapa 1 — escolha o algoritmo para organizar o lote (seed 2042):")
        print("  1. Bubble Sort   2. Merge Sort   3. Quick Sort")
        alg = {"1": "bubble", "2": "merge", "3": "quick"}[ler_opcao(["1", "2", "3"])]
        f.reiniciar()
        f.etapa_lote(algoritmo=alg)
        print("\n  Etapa 2 — triagem: " + ("usando as SUAS ações da Fase 2, que o solver vai conferir."
              if self.fase2.venceu() else "você ainda não resolveu a Fase 2; o solver (BFS) vai resolver."))
        f.etapa_triagem(self.fase2.acoes_feitas if self.fase2.venceu() else None)
        print("  Etapa 3 — mapa: " + ("usando a SUA trilha da Fase 3, que o solver vai conferir."
              if self.fase3.venceu() else "você ainda não resolveu a Fase 3; o solver (BFS) vai resolver."))
        f.etapa_mapa(self.fase3.trilha if self.fase3.venceu() else None)
        print("  Etapa 4 — comparando BFS e DFS em dois cenários...")
        f.comparar_estrategias()
        print("\n" + f.relatorio_texto())
        try:
            caminho = f.gravar_relatorio()
            print(f"\n  Relatório gravado em: {caminho}")
        except OSError:
            print("\n  (Não foi possível gravar o relatório em arquivo.)")
        if f.venceu():
            print("\n  Selo 5 conquistado!")
        if all(self.selos()):
            titulo("COFRE DE VERIFICAÇÃO ABERTO")
            for paragrafo in narrativa.EPILOGO:
                print(textwrap.fill(paragrafo, 68, initial_indent="  ", subsequent_indent="  "))
            print("\n  Missão cumprida, Analista!")
        elif f.venceu():
            faltam = [str(i) for i, s in enumerate(self.selos(), 1) if not s]
            print(f"  Para abrir o Cofre de Verificação, conquiste também o(s) selo(s): {', '.join(faltam)}.")
        pausa()

    # ======================================================== outros
    def abrir_visualizacao(self):
        """Gera visualizacao.html com os algoritmos reais e abre no navegador (sem internet)."""
        import pathlib
        import webbrowser
        from interface.visualizacao import gerar_html
        print("\n  Gerando a visualização (executando os algoritmos)...")
        caminho = gerar_html()
        print(f"  Arquivo: {caminho}")
        try:
            webbrowser.open(pathlib.Path(caminho).as_uri())
            print("  Aberto no navegador. Se não abrir, dê dois cliques no arquivo acima.")
        except Exception:
            print("  Não consegui abrir o navegador; dê dois cliques no arquivo acima.")
        pausa()

    def instrucoes(self):
        titulo("INSTRUÇÕES")
        print("  - Escolha as opções digitando o número e teclando Enter.")
        print("  - Cada fase tem um objetivo, regras e um selo. Junte 5 selos.")
        print("  - Jogadas inválidas são recusadas com explicação e não alteram nada.")
        print("  - Você pode reiniciar uma fase sem reiniciar o jogo.")
        print("  - Nas Fases 2 e 3 é possível desfazer ações (pilha do histórico).")
        print("  - Em 'Resolver', o computador resolve as Fases 2 e 3 com BFS ou DFS.")
        print("  - Na Fase 4 você prevê as rotações da árvore AVL e decide quando dois")
        print("    estados são o mesmo. Na Fase 5 o sistema confere tudo e emite o relatório.")
        print(f"  - Os dados são gerados com seed fixa ({self.seed}): a partida é reproduzível.")
        pausa()

    def resultados(self):
        titulo("RESULTADOS")
        print("  " + self.barra_de_selos())
        print("\n  Fase 1 — tentativas de ordenação:")
        if not self.fase1.tentativas:
            print("    (nenhuma)")
        for alg, crit, c, aceito in self.fase1.tentativas:
            print(f"    {c.algoritmo:12} por {crit:9}: {c.comparacoes:>5} comparações, "
                  f"{c.movimentacoes:>5} movimentações -> {'ACEITO' if aceito else 'recusado'}")
        print("\n  Fase 2 — ações válidas realizadas:")
        print("    " + (", ".join(f"{a} {e}" for a, e in self.fase2.acoes_feitas) or "(nenhuma)"))
        print("\n  Fase 3 — trilha percorrida:")
        print(f"    {' -> '.join(self.fase3.trilha)}  (energia restante: {self.fase3.estado[3]})")
        print("\n  Fase 4 — cofre:")
        print(f"    Sala 1: {self.fase4.proximo}/{len(self.fase4.sequencia)} lacres, "
              f"{self.fase4.acertos_sala1()} previsões corretas; altura da AVL {self.fase4.avl.altura()}")
        print(f"    Sala 2: {sum(self.fase4.respostas_sala2.values())}/{len(self.fase4.pares)} pares corretos")
        print("\n  Fase 5 — auditoria: " + ("consistente" if self.fase5.venceu() else
              "não executada" if not self.fase5.etapas else "NÃO consistente"))
        pausa()
