"""
Interface em terminal (texto). Só exibe e lê opções: NENHUMA regra do jogo
fica aqui. As regras moram em jogo/ (separação exigida na seção 12).
"""

from jogo.fase1 import Fase1
from jogo.fase2 import Fase2, EVIDENCIAS, proximo_esperado
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

    def selos(self):
        return [self.fase1.selo, self.fase2.venceu(), False, False, False]

    def barra_de_selos(self):
        return "  ".join(f"[{'X' if s else ' '}] Selo {i}" for i, s in enumerate(self.selos(), 1))

    # ======================================================== menu inicial
    def executar(self):
        titulo("URNA LÓGICA — O Enigma da Eleição de Verídia")
        print("  Ano 2042. Uma falha de sincronização embaralhou a auditoria de Verídia.")
        print("  Você é Analista de Integridade de Dados da Comissão Independente de")
        print("  Verificação (CIV). Recupere os 5 selos e chegue ao Cofre de Verificação.")
        print("  (Cidade, registros e códigos são inteiramente fictícios.)")
        while True:
            titulo("MENU INICIAL")
            print("  " + self.barra_de_selos())
            print("\n  1. Jogar\n  2. Resolver (solver automático)\n  3. Instruções\n  4. Resultados\n  0. Sair")
            op = ler_opcao(["1", "2", "3", "4", "0"])
            if op == "1":
                self.menu_jogar()
            elif op == "2":
                self.menu_resolver()
            elif op == "3":
                self.instrucoes()
            elif op == "4":
                self.resultados()
            else:
                print("\nAté a próxima auditoria!")
                return

    def menu_jogar(self):
        while True:
            titulo("ESCOLHA A FASE")
            print("  1. " + Fase1.NOME + ("  (selo obtido)" if self.fase1.selo else ""))
            print("  2. " + Fase2.NOME + ("  (selo obtido)" if self.fase2.venceu() else ""))
            print("  3. Fase 3 — O Mapa das Seções       (em construção)")
            print("  4. Fase 4 — O Cofre dos Estados     (em construção)")
            print("  5. Fase 5 — A Auditoria Final       (em construção)")
            print("  0. Voltar")
            op = ler_opcao(["1", "2", "3", "4", "5", "0"])
            if op == "1":
                self.jogar_fase1()
            elif op == "2":
                self.jogar_fase2()
            elif op == "0":
                return
            else:
                print("  Esta fase será liberada nas próximas versões.")

    def menu_resolver(self):
        titulo("SOLVER")
        print("  O solver (BFS e DFS) será liberado junto com a Fase 3.")
        pausa()

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

    # ======================================================== outros
    def instrucoes(self):
        titulo("INSTRUÇÕES")
        print("  - Escolha as opções digitando o número e teclando Enter.")
        print("  - Cada fase tem um objetivo, regras e um selo. Junte 5 selos.")
        print("  - Jogadas inválidas são recusadas com explicação e não alteram nada.")
        print("  - Você pode reiniciar uma fase sem reiniciar o jogo.")
        print("  - Na Fase 2 é possível desfazer ações (pilha do histórico).")
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
        pausa()
