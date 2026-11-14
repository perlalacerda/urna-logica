"""
Dicas e orientação ao jogador ("o que fazer agora").

Ideia didática: nas Fases 2 e 3, a dica NÃO está escrita à mão.
Ela é calculada pelo próprio solver (BFS) a partir da situação atual do
jogador: a BFS encontra o caminho mais curto até o objetivo e a dica é o
primeiro passo desse caminho. Se não houver caminho, a dica diz isso —
e sugere desfazer.

Nenhuma regra nova mora aqui: só chamadas às funções das fases e do solver.
"""

from algoritmos.solver import bfs
from algoritmos.ordenacao import primeiro_fora_de_ordem
from jogo.fase1 import CHAVE_AUDITORIA
from jogo.fase2 import ProblemaTriagem, proximo_esperado
from jogo.fase3 import ProblemaMapa, LOCAIS, DESTINO


# ---------------------------------------------------- problemas que começam no estado atual
class _TriagemDaqui(ProblemaTriagem):
    def __init__(self, estado, entrada, alvo):
        super().__init__(entrada, alvo)
        self._inicio = estado

    def estado_inicial(self):
        return self._inicio


class _MapaDaqui(ProblemaMapa):
    def __init__(self, estado, G):
        super().__init__(G=G)
        self._inicio = estado

    def estado_inicial(self):
        return self._inicio


# ---------------------------------------------------- Fase 1
def orientacao_fase1(f):
    if f.selo:
        return "Fase concluída. Volte (0) e escolha a próxima fase."
    if not f.tentativas:
        return "Leia o enigma (1) e depois ordene o lote (2), escolhendo um algoritmo e um critério."
    return "O lote foi recusado. Tente de novo (2) com outro critério."


def dica_fase1(f):
    if f.selo:
        return "Esta fase já está concluída."
    if f.tentativas and f.tentativas[-1][1] != "auditoria":
        return ("O critério escolhido não segue a regra da auditoria. A regra pede ZONA primeiro, "
                "depois SEÇÃO, depois HORÁRIO: escolha o critério 4.")
    return ("Qualquer um dos três algoritmos serve; o que decide é o CRITÉRIO. "
            "Escolha o critério 4 (zona, seção, horário). O algoritmo muda só o trabalho feito.")


# ---------------------------------------------------- Fase 2
def orientacao_fase2(f):
    if f.venceu():
        return "Custódia completa. Volte (0) e escolha a próxima fase."
    esperado = proximo_esperado(tuple(f.custodia.percorrer()), f.alvo)
    ok_f, frente = f.fila.peek()
    ok_p, topo = f.pilha.peek()
    partes = [f"A custódia espera {esperado}."]
    if ok_f:
        partes.append(f"A 1ª da fila é {frente}.")
    if ok_p:
        partes.append(f"O topo da pilha é {topo}.")
    partes.append("Escolha a ação que leva cada evidência ao lugar certo (? = dica).")
    return " ".join(partes)


def dica_fase2(f):
    """O solver (BFS) parte da situação atual e sugere o 1º passo do caminho mais curto."""
    if f.venceu():
        return "Esta fase já está concluída."
    r = bfs(_TriagemDaqui(f.estado(), f.entrada, f.alvo))
    if not r.encontrou:
        return "Desta situação não há como completar a custódia. Use desfazer (5) ou reinicie (6)."
    acao = r.caminho[1][0]
    nomes = {"aceitar": "1 (aceitar)", "guardar": "2 (guardar)", "arquivar": "3 (arquivar)", "liberar": "4 (liberar)"}
    falta = r.numero_acoes()
    return (f"O solver (BFS) sugere: {nomes[acao]}. "
            f"A partir daqui faltam {falta} ação(ões) no caminho mais curto.")


# ---------------------------------------------------- Fase 3
def orientacao_fase3(f):
    pos, pistas, _, energia = f.estado
    if f.venceu():
        return "Você chegou ao Centro de Validação. Volte (0) e escolha a próxima fase."
    if energia == 0:
        return "Sua energia acabou. Desfaça (U) ou reinicie (R)."
    if "SEQ" not in pistas:
        return (f"Você está em {pos}. Primeiro pegue a pista SEQ na Unidade Oeste (E): ela abre o "
                "Arquivo Oeste (H), o caminho até a pista AUT em D. Digite a letra de um vizinho (? = dica).")
    if "AUT" not in pistas:
        return (f"Você está em {pos} e já tem SEQ. Agora pegue a pista AUT na Unidade Leste (D), "
                "passando pelo Arquivo Oeste (H). Digite a letra de um vizinho (? = dica).")
    return f"Você já tem AUT. Siga até o Centro de Validação ({DESTINO}). Digite a letra de um vizinho."


def dica_fase3(f):
    """O solver (BFS) parte da posição atual (com as pistas e a energia atuais)."""
    if f.venceu():
        return "Esta fase já está concluída."
    r = bfs(_MapaDaqui(f.estado, f.G))
    if not r.encontrou:
        return ("Daqui não dá para chegar ao destino com a energia que resta. "
                "Desfaça alguns movimentos (U) ou reinicie (R).")
    prox = r.caminho[1][1][0]
    return (f"O solver (BFS) sugere ir para {prox} ({LOCAIS[prox]}). "
            f"Pelo caminho mais curto faltam {r.numero_acoes()} movimento(s).")


# ---------------------------------------------------- Fase 4
def orientacao_fase4(f):
    if f.venceu():
        return "Cofre organizado. Volte (0) e vá para a Fase 5."
    if not f.sala1_completa():
        return f"Entre na Sala 1 (1) e insira os lacres: faltam {len(f.sequencia) - f.proximo}."
    if not f.sala2_completa():
        return "Sala 1 completa. Agora responda os pares da Sala 2 (2)."
    return "Volte (0)."


def dica_fase4_sala1():
    return ("Imagine o novo código entrando na árvore: desça comparando (menor vai para a esquerda, "
            "maior para a direita). Depois, suba conferindo cada nó: se um lado ficou 2 níveis mais alto, "
            "há rotação. Mesmo lado duas vezes (esq-esq ou dir-dir) = rotação simples (RD/RE); "
            "lados trocados (esq-dir ou dir-esq) = rotação dupla (RED/RDE).")


def dica_fase4_sala2():
    return ("A chave do cofre é (posição, pistas, portas). Se algum desses três mudar, são situações "
            "diferentes. Se os três forem iguais, só vale explorar de novo quem tem MAIS energia.")


# ---------------------------------------------------- Fase 5
def orientacao_fase5(selos):
    faltam = [str(i) for i, s in enumerate(selos[:4], 1) if not s]
    if faltam:
        return (f"A auditoria final confere tudo. As fases {', '.join(faltam)} ainda não foram resolvidas por você; "
                "nelas o solver resolve e o sistema confere.")
    return "Você resolveu as fases 1 a 4. A auditoria final vai conferir as SUAS jogadas."


def lote_ok(f):
    return primeiro_fora_de_ordem(f.registros, CHAVE_AUDITORIA) == -1


# ---------------------------------------------------- Desafio extra: mapa com custos (aula 11)
def dica_mapa_custos(f):
    """Dica pelo DIJKSTRA a partir da situação atual: o caminho de MENOR ENERGIA."""
    from algoritmos.dijkstra import dijkstra_estados
    if f.venceu():
        return "Desafio concluído."
    r = dijkstra_estados(_MapaDaqui(f.estado, f.G))
    if not r.encontrou:
        return ("Daqui não dá para chegar ao destino com a energia que resta. "
                "Desfaça alguns movimentos (U) ou reinicie (R).")
    prox = r.caminho[1][1][0]
    return (f"O Dijkstra sugere ir para {prox} ({LOCAIS[prox]}). "
            f"Pelo caminho mais barato, daqui ainda se gastam {r.custo} de energia "
            f"em {r.numero_acoes()} movimento(s).")


def orientacao_mapa_custos(f):
    pos, pistas, _, energia = f.estado
    if f.venceu():
        return "Desafio concluído. Compare sua rota com BFS, guloso e Dijkstra (T)."
    if "SEQ" not in pistas:
        alvo = "Busque a pista SEQ na Unidade Oeste (E)."
    elif "AUT" not in pistas:
        alvo = "Com SEQ, a porta do Arquivo Oeste (H) abre. Busque AUT na Unidade Leste (D)."
    else:
        alvo = "Com AUT, siga para o Centro de Validação (F)."
    return (f"{alvo} Energia restante: {energia}. Olhe o custo de cada corredor antes de andar. "
            "Digite a letra de um vizinho (? = dica).")
