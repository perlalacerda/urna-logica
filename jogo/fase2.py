"""
FASE 2 — A Central de Triagem                        (seção 6 do enunciado)

Conceitos: FILA (ordem de chegada), PILHA (espera temporária e desfazer),
LISTA LIGADA (trilha de custódia).

    FILA de entrada         PILHA de espera          LISTA de custódia
    E1 E2 E3 E4 E5 E6  -->  topo -> ...         -->  E2 -> E4 -> E1 -> E6
    (só o 1º pode sair)     (só o topo sai)          (cresce pelo fim)

    + ARQUIVO: evidências que não fazem parte da custódia (E3, E5).

Objetivo (enigma 6.3): montar a custódia na sequência  E2 -> E4 -> E1 -> E6.

REGRAS (cada uma é uma função que recebe a estrutura e o elemento e devolve
(True, "") ou (False, motivo) — exigência do item 6.3):

  R1 ACEITAR  : o 1º da fila vai para a custódia
                só se ele for o PRÓXIMO esperado da sequência.
  R2 GUARDAR  : o 1º da fila vai para o topo da pilha
                só se ele fizer parte da custódia
                e for necessário ANTES do elemento que está no topo.
                (Isso impede "enterrar" uma evidência sob outra que
                 só pode sair depois dela — o beco sem saída da pilha.)
  R3 ARQUIVAR : o 1º da fila vai para o arquivo
                só se ele NÃO fizer parte da custódia.
  R4 LIBERAR  : o topo da pilha vai para a custódia
                só se ele for o PRÓXIMO esperado.
  R5 DESFAZER : volta ao estado anterior à última ação válida (pilha LIFO).

Vitória: custódia = E2, E4, E1, E6  e  fila e pilha vazias.

Uma tentativa inválida NÃO altera nada (item 6.4).

O enigma não está escrito no código: as regras só olham o estado atual.
Por isso o mesmo módulo serve ao jogador (modo manual) e ao solver.
"""

from estruturas.fila import Fila
from estruturas.pilha import Pilha
from estruturas.lista_ligada import ListaLigada

EVIDENCIAS = {
    "E1": "Log do Arquivo Norte",
    "E2": "Lacre da urna da seção 014",
    "E3": "Cópia de teste (descartável)",
    "E4": "Boletim parcial da zona 03",
    "E5": "Rascunho duplicado (descartável)",
    "E6": "Assinatura do Centro de Validação",
}
ENTRADA_PADRAO = ("E1", "E2", "E3", "E4", "E5", "E6")
ALVO_PADRAO = ("E2", "E4", "E1", "E6")


# ======================================================== REGRAS (funções)
def proximo_esperado(custodia, alvo):
    """Qual evidência deve entrar agora na custódia? (None se completa)"""
    n = len(custodia)
    return alvo[n] if n < len(alvo) else None


def regra_aceitar(custodia, alvo, evidencia):
    """R1 — evidência sai da fila direto para a custódia."""
    esperado = proximo_esperado(custodia, alvo)
    if evidencia == esperado:
        return True, ""
    if evidencia not in alvo:
        return False, f"{evidencia} não faz parte da custódia; arquive-a."
    return False, f"A custódia espera {esperado} agora, não {evidencia}."


def regra_guardar(pilha, alvo, evidencia):
    """R2 — evidência sai da fila para o topo da pilha de espera."""
    if evidencia not in alvo:
        return False, f"{evidencia} não faz parte da custódia; não precisa esperar na pilha."
    ok, topo = pilha.peek()
    if ok and alvo.index(evidencia) > alvo.index(topo):
        return False, (f"{evidencia} ficaria sobre {topo}, mas {topo} precisa sair antes. "
                       f"Na pilha, só sai quem está no topo (LIFO).")
    return True, ""


def regra_arquivar(alvo, evidencia):
    """R3 — evidência sai da fila para o arquivo."""
    if evidencia in alvo:
        return False, f"{evidencia} faz parte da custódia; não pode ser arquivada."
    return True, ""


def regra_liberar(custodia, alvo, topo):
    """R4 — evidência sai do topo da pilha para a custódia."""
    esperado = proximo_esperado(custodia, alvo)
    if topo == esperado:
        return True, ""
    return False, f"O topo da pilha é {topo}, mas a custódia espera {esperado}."


# ======================================================== A FASE
class Fase2:
    NOME = "Fase 2 — A Central de Triagem"
    ABERTURA = ("Os registros foram organizados.\n"
                "Agora precisamos movimentar as evidências sem quebrar a sequência de processamento.\n"
                "Atenção: algumas ações podem ser desfeitas; outras obedecem à ordem de chegada.")
    ACOES = ("aceitar", "guardar", "arquivar", "liberar")

    def __init__(self, entrada=ENTRADA_PADRAO, alvo=ALVO_PADRAO):
        self.entrada = tuple(entrada)
        self.alvo = tuple(alvo)
        self.reiniciar()

    def reiniciar(self):
        self.fila = Fila()
        for e in self.entrada:
            self.fila.enqueue(e)
        self.pilha = Pilha()             # pilha de espera
        self.custodia = ListaLigada()    # lista de custódia
        self.arquivo = []
        self.historico = Pilha()         # pilha do DESFAZER: guarda "fotos" do estado
        self.acoes_feitas = []           # registro legível para o relatório

    # ---------------------------------------------------- estado
    def estado(self):
        """
        "Fotografia" do estado como tupla imutável e comparável:
            (fila, pilha [topo primeiro], custódia)
        O arquivo não precisa entrar: ele é tudo o que não está nas outras três.
        Duas situações com a mesma tupla são o MESMO estado do jogo.
        """
        return (tuple(self.fila.para_lista()),
                tuple(self.pilha.para_lista()),
                tuple(self.custodia.percorrer()))

    def _restaurar(self, estado):
        fila, pilha, custodia = estado
        self.fila = Fila()
        for e in fila:
            self.fila.enqueue(e)
        self.pilha = Pilha()
        for e in reversed(pilha):        # empilha da base para o topo
            self.pilha.push(e)
        self.custodia = ListaLigada()
        for e in custodia:
            self.custodia.inserir_fim(e)
        usados = set(fila) | set(pilha) | set(custodia)
        self.arquivo = [e for e in self.entrada if e not in usados]

    def venceu(self):
        return (tuple(self.custodia.percorrer()) == self.alvo
                and self.fila.esta_vazia() and self.pilha.esta_vazia())

    # ---------------------------------------------------- ações
    def validar(self, acao):
        """Confere se a ação é permitida AGORA. Devolve (ok, motivo)."""
        custodia = tuple(self.custodia.percorrer())
        if acao in ("aceitar", "guardar", "arquivar"):
            ok, frente = self.fila.peek()
            if not ok:
                return False, "A fila de entrada está vazia."
            if acao == "aceitar":
                return regra_aceitar(custodia, self.alvo, frente)
            if acao == "guardar":
                return regra_guardar(self.pilha, self.alvo, frente)
            return regra_arquivar(self.alvo, frente)
        if acao == "liberar":
            ok, topo = self.pilha.peek()
            if not ok:
                return False, "A pilha de espera está vazia."
            return regra_liberar(custodia, self.alvo, topo)
        return False, f"Ação desconhecida: '{acao}'. Use: {', '.join(self.ACOES)} ou desfazer."

    def executar(self, acao):
        """Valida e, se permitido, executa. Devolve (ok, mensagem)."""
        ok, motivo = self.validar(acao)
        if not ok:
            return False, "Movimento recusado: " + motivo     # nada foi alterado

        self.historico.push(self.estado())      # foto ANTES da ação, para desfazer
        if acao == "aceitar":
            _, e = self.fila.dequeue()
            self.custodia.inserir_fim(e)
            msg = f"{e} saiu da fila e entrou na custódia."
        elif acao == "guardar":
            _, e = self.fila.dequeue()
            self.pilha.push(e)
            msg = f"{e} saiu da fila e foi para o topo da pilha de espera."
        elif acao == "arquivar":
            _, e = self.fila.dequeue()
            self.arquivo.append(e)
            msg = f"{e} saiu da fila e foi arquivada."
        else:  # liberar
            _, e = self.pilha.pop()
            self.custodia.inserir_fim(e)
            msg = f"{e} saiu do topo da pilha e entrou na custódia."
        self.acoes_feitas.append((acao, e))
        if self.venceu():
            msg += "\nCustódia completa: " + " -> ".join(self.alvo) + ". Selo 2 conquistado!"
        return True, msg

    def desfazer(self):
        """
        R5 — desfaz a ÚLTIMA ação válida: o estado mais recente guardado
        na pilha do histórico é o primeiro a ser restaurado (LIFO).
        """
        ok, anterior = self.historico.pop()
        if not ok:
            return False, "Não há ação para desfazer."
        self._restaurar(anterior)
        acao, e = self.acoes_feitas.pop()
        return True, f"Desfeito: {acao} {e}."

    # ---------------------------------------------------- para o solver
    @classmethod
    def a_partir_do_estado(cls, estado, entrada=ENTRADA_PADRAO, alvo=ALVO_PADRAO):
        f = cls(entrada, alvo)
        f._restaurar(estado)
        return f

    def sucessores(self):
        """
        Todos os estados alcançáveis com UMA ação válida a partir do atual.
        Devolve [(acao, novo_estado)]. É a "lista de adjacência" do
        grafo de estados, gerada sob demanda (grafo implícito).
        Usa exatamente as mesmas regras do jogador.
        """
        resultado = []
        for acao in self.ACOES:
            if self.validar(acao)[0]:
                copia = Fase2.a_partir_do_estado(self.estado(), self.entrada, self.alvo)
                copia.executar(acao)
                resultado.append((acao, copia.estado()))
        return resultado

    def eh_objetivo(self):
        return self.venceu()
