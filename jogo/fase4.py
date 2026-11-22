"""
FASE 4 — O Cofre dos Estados                         (seção 8 do enunciado)

Conceitos: árvore AVL (busca, inserção, rotações, altura, fator de
balanceamento) e CHAVE DE ESTADO.

Três salas do cofre:

  SALA 1 — "Lacres do cofre" (inserção e rotações)
      O cofre indexa os códigos dos lacres numa AVL. Antes de cada inserção,
      o jogador PREVÊ o que vai acontecer: nenhuma rotação, RD, RE, RED ou RDE.
      A sequência é a mesma do exemplo da aula 08 (slides 9-15):
          70, 50, 40, 80, 90, 15, 25, 45, 42
      e provoca as quatro rotações. O jogo mostra a árvore antes e depois,
      com altura (h) e fator de balanceamento (FB) de cada nó.

  SALA 2 — "O estado que parece igual" (enigma 8.2)
      Pares de situações do mapa. Para cada par, o jogador responde se elas
      têm a MESMA configuração (posição, pistas, portas) e se o solver deve
      explorar a segunda. A chave da AVL é o estado inteiro, energia incluída
      (chave_estado); "não explorar" vale para a chave idêntica (repetido) e,
      com a melhoria de dominância, para a mesma configuração com menos energia.
      As respostas certas NÃO estão escritas no código: são calculadas com as
      funções do solver (chave_estado e configuracao).

  SALA 3 — "Consulta ao cofre" (busca existente e inexistente)
      O jogador procura códigos; o jogo mostra o caminho percorrido na
      árvore e quantas comparações foram feitas (no máximo altura + 1).

Selo 4: Sala 1 completa (todas as inserções feitas) e Sala 2 toda correta.
"""

from estruturas.avl import ArvoreAVL
from jogo.fase3 import chave_estado, configuracao, rotulo

SEQUENCIA_LACRES = (70, 50, 40, 80, 90, 15, 25, 45, 42)
OPCOES_ROTACAO = ("nenhuma", "RD", "RE", "RED", "RDE")

# Pares de situações do mapa: (estado já visto, estado novo)
PARES_ESTADOS = (
    (("C", (), (), 9), ("C", ("SEQ",), (), 7)),               # mesma posição, pistas diferentes
    (("B", ("SEQ",), (), 6), ("B", ("SEQ",), (), 4)),         # mesma configuração, menos energia
    (("D", ("AUT", "SEQ"), ("H",), 4), ("D", ("AUT", "SEQ"), ("H",), 6)),   # mesma configuração, MAIS energia
    (("H", ("SEQ",), ("H",), 5), ("B", ("SEQ",), ("H",), 5)),  # posições diferentes
)


def resposta_correta(visto, novo):
    """
    Calculada com as MESMAS funções do solver:
      mesma_conf = configuracao(visto) == configuracao(novo)
      explorar   = configurações diferentes OU energia do novo > energia do visto
    (com a energia igual, as chaves são idênticas: repetido; com a energia menor,
    o novo é dominado e a melhoria de dominância não o expande)
    """
    mesma_conf = configuracao(visto) == configuracao(novo)
    explorar = (not mesma_conf) or novo[3] > visto[3]
    return mesma_conf, explorar


def explicar(visto, novo):
    mesma, explorar = resposta_correta(visto, novo)
    if not mesma:
        dif = []
        if visto[0] != novo[0]:
            dif.append("a posição")
        if visto[1] != novo[1]:
            dif.append("as pistas")
        if visto[2] != novo[2]:
            dif.append("as portas")
        motivo = ("os vizinhos são outros" if visto[0] != novo[0]
                  else "pistas diferentes abrem portas diferentes")
        return (f"Situações diferentes: muda(m) {' e '.join(dif)}. Permitem ações diferentes "
                f"({motivo}). As chaves são diferentes e o solver explora as duas.")
    if explorar:
        return ("Mesmo lugar, mesmas pistas e portas; só a energia muda, então a chave é outra. "
                "Com MAIS energia, dá para ir mais longe: o solver explora.")
    if chave_estado(visto) == chave_estado(novo):
        return "Chave idêntica, energia inclusive: estado repetido. O solver NÃO expande de novo."
    return ("Mesmo lugar, mesmas pistas e portas, com MENOS energia: a chave é outra (a energia faz "
            "parte dela), mas tudo o que o novo faria, o antigo já fazia. Com a melhoria de "
            "dominância, o solver NÃO expande.")


class Fase4:
    NOME = "Fase 4 — O Cofre dos Estados"
    ABERTURA = ("O sistema está explorando caminhos repetidos.\n"
                "Para não investigar a mesma configuração indefinidamente, precisamos\n"
                "reconhecer estados já visitados. O cofre só abre quando a memória do\n"
                "sistema estiver organizada.")

    def __init__(self, sequencia=SEQUENCIA_LACRES, pares=PARES_ESTADOS):
        self.sequencia = tuple(sequencia)
        self.pares = tuple(pares)
        self.reiniciar()

    def reiniciar(self):
        self.avl = ArvoreAVL()
        self.proximo = 0               # índice do próximo lacre a inserir
        self.previsoes = []            # (código, previsto, ocorrido, acertou)
        self.respostas_sala2 = {}      # índice do par -> acertou?

    # ---------------------------------------------------- sala 1
    def sala1_completa(self):
        return self.proximo >= len(self.sequencia)

    def inserir_proximo(self, previsao):
        """
        Insere o próximo lacre e compara a previsão do jogador com a rotação
        que de fato ocorreu. Devolve um dicionário para a interface.
        """
        if self.sala1_completa():
            return {"ok": False, "mensagem": "Todos os lacres já foram inseridos."}
        if previsao not in OPCOES_ROTACAO:
            return {"ok": False, "mensagem": f"Previsão inválida: {previsao}."}
        codigo = self.sequencia[self.proximo]
        antes = self.avl.desenhar()
        n_rot = len(self.avl.historico_rotacoes)
        self.avl.inserir(codigo)
        novas = self.avl.historico_rotacoes[n_rot:]
        ocorrido = novas[0][0] if novas else "nenhuma"
        no_desbalanceado = novas[0][1] if novas else None
        acertou = previsao == ocorrido
        explicacao = explicar_rotacao(ocorrido, no_desbalanceado, codigo, len(self.avl))
        self.previsoes.append((codigo, previsao, ocorrido, acertou))
        self.proximo += 1
        return {"ok": True, "codigo": codigo, "antes": antes, "depois": self.avl.desenhar(),
                "ocorrido": ocorrido, "no": no_desbalanceado, "acertou": acertou,
                "explicacao": explicacao,
                "altura": self.avl.altura(), "eh_avl": self.avl.eh_avl()}

    def acertos_sala1(self):
        return sum(1 for *_, ok in self.previsoes if ok)

    # ---------------------------------------------------- sala 2
    def responder_par(self, indice, mesma_chave, explorar):
        visto, novo = self.pares[indice]
        certo_chave, certo_explorar = resposta_correta(visto, novo)
        acertou = (mesma_chave == certo_chave) and (explorar == certo_explorar)
        self.respostas_sala2[indice] = acertou
        return acertou, explicar(visto, novo), (certo_chave, certo_explorar)

    def sala2_completa(self):
        return len(self.respostas_sala2) == len(self.pares) and all(self.respostas_sala2.values())

    # ---------------------------------------------------- sala 3
    def consultar(self, codigo):
        achou, _, comparacoes = self.avl.buscar(codigo)
        return achou, self.avl.caminho_busca(codigo), comparacoes

    # ---------------------------------------------------- selo
    def venceu(self):
        return self.sala1_completa() and self.sala2_completa()


def explicar_rotacao(ocorrido, no, codigo, quantidade):
    """Explica POR QUE houve (ou não) rotação, nos termos da aula 08."""
    if ocorrido == "nenhuma":
        if quantidade < 3:
            return ("Com menos de 3 nós nenhuma rotação é possível: para um nó ficar com "
                    "FB = ±2, um lado precisa ter altura 1 e o outro ser vazio (altura -1).")
        return (f"Depois de inserir {codigo}, todos os nós do caminho até a raiz ficaram "
                f"com FB entre -1 e +1. A árvore continua AVL sem rotação.")
    casos = {
        "RD": (f"O nó {no} ficou com FB = +2 (esquerda mais alta) e {codigo} entrou na "
               f"esquerda do filho esquerdo: caso \"reta\" -> Rotação Direita."),
        "RE": (f"O nó {no} ficou com FB = -2 (direita mais alta) e {codigo} entrou na "
               f"direita do filho direito: caso \"reta\" -> Rotação Esquerda."),
        "RED": (f"O nó {no} ficou com FB = +2 e {codigo} entrou na DIREITA do filho esquerdo: "
                f"caso \"curva\" -> rotação dupla Esquerda-Direita (RE no filho, depois RD em {no})."),
        "RDE": (f"O nó {no} ficou com FB = -2 e {codigo} entrou na ESQUERDA do filho direito: "
                f"caso \"curva\" -> rotação dupla Direita-Esquerda (RD no filho, depois RE em {no})."),
    }
    return casos[ocorrido]


def descrever_par(par):
    visto, novo = par
    return f"Já visto: {rotulo(visto)}\n  Novo    : {rotulo(novo)}"
