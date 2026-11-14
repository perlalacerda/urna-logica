"""
DESAFIO EXTRA — O Mapa com Custos                 (Aula 11 — Algoritmos Gulosos)

Variante da Fase 3 criada pela equipe (não faz parte do enunciado; o item 7.4
permite: "cada movimento pode consumir uma unidade ou ter custo definido por
você"). A Fase 3 original continua igual, com todo movimento custando 1.

MESMO MAPA, MESMAS PISTAS E PORTAS, mas cada corredor tem um custo de energia:

    Corredor  Custo        Corredor  Custo
    A-B       1            C-G       2
    A-C       6  (em obras) D-F       2
    B-C       1            D-H       2
    B-H       2            F-G       5
    B-I       2            G-I       1
    C-E       1

    Energia inicial: 15.

O QUE O DESAFIO MOSTRA (números conferidos em testes/test_mapa_custos.py)
    BFS      : A-C-E-C-B-H-D-F  -> 7 movimentos, 15 de energia (gasta tudo)
    Dijkstra : A-B-C-E-C-B-H-D-F -> 8 movimentos, 11 de energia (sobram 4)
    Guloso   : A-B-C-E-C-B-A     -> trava na Central sem movimento novo

    1. Menos movimentos (BFS) não é o mesmo que menos energia (Dijkstra):
       a BFS pega o atalho A-C porque conta arestas, sem olhar o custo 6.
    2. O guloso "corredor mais barato" escolhe bem cada passo isolado e,
       mesmo assim, fica preso — como o troco de 19 com moedas {2, 3, 6}
       (6+6+6 deixa 1 sem moeda; 6+6+3+2+2 resolveria).
    3. O Dijkstra também é guloso, mas escolhe pelo custo TOTAL desde a
       origem (d[u]), e por isso a escolha dele é segura com pesos >= 0.
    4. O Dijkstra no grafo puro (sem portas) acha A-B-H-D-F com custo 7,
       mas essa rota atravessa a porta H sem a pista SEQ: o enigma exige
       buscar no ESPAÇO DE ESTADOS, como na Fase 3.
"""

from estruturas.grafo import Grafo
from algoritmos.solver import bfs
from algoritmos.dijkstra import dijkstra, dijkstra_estados, guloso_ingenuo
from jogo.fase3 import Fase3, ProblemaMapa, LOCAIS, INICIO, DESTINO, estado_inicial

PESOS = {("A", "B"): 1, ("A", "C"): 6, ("B", "C"): 1, ("B", "H"): 2, ("B", "I"): 2,
         ("C", "E"): 1, ("C", "G"): 2, ("D", "F"): 2, ("D", "H"): 2, ("F", "G"): 5,
         ("G", "I"): 1}
ENERGIA_CUSTOS = 15


def construir_mapa_custos(pesos=PESOS, locais=LOCAIS):
    G = Grafo(orientado=False)
    for v, nome in locais.items():
        G.adicionar_vertice(v, nome)
    for (u, v), w in pesos.items():
        G.adicionar_aresta(u, v, w)
    return G


def problema_custos(energia=ENERGIA_CUSTOS):
    return ProblemaMapa(construir_mapa_custos(), energia=energia)


def comparar(energia=ENERGIA_CUSTOS):
    """BFS, guloso ingênuo e Dijkstra no mesmo mapa com custos."""
    P = problema_custos(energia)
    return [alg(P) for alg in (bfs, guloso_ingenuo, dijkstra_estados)]


def dijkstra_grafo_puro():
    """Dijkstra da aula no grafo SEM pistas e portas, a partir de A."""
    G = construir_mapa_custos()
    d, pi, S, passos = dijkstra(G, INICIO)
    caminho, v = [], DESTINO
    while v is not None:
        caminho.append(v)
        v = pi[v]
    return d, pi, S, passos, list(reversed(caminho))


def custo_do_caminho(caminho):
    """Soma dos custos dos corredores de uma sequência de locais."""
    G = construir_mapa_custos()
    return sum(G.peso(u, v) for u, v in zip(caminho, caminho[1:]))


class FaseMapaCustos(Fase3):
    """O jogador joga o mapa com custos. As regras são as MESMAS da Fase 3."""

    NOME = "Desafio extra — O Mapa com Custos (Aula 11)"
    ABERTURA = ("Os corredores de Verídia não custam todos o mesmo: alguns estão em obras e\n"
                "consomem mais energia. Chegue ao Centro de Validação com a autenticação,\n"
                "gastando o mínimo possível. Será que o atalho é o caminho mais barato?")

    def __init__(self, energia=ENERGIA_CUSTOS):
        super().__init__(energia)
        self.G = construir_mapa_custos()
        self.reiniciar()
        self._otimo = dijkstra_estados(problema_custos(energia)).custo

    def gasto(self):
        return self.energia_inicial - self.estado[3]

    def ir_para(self, v):
        ok, msg = super().ir_para(v)
        if ok and self.venceu():
            msg = msg.replace("Selo 3 conquistado!", "").rstrip()
            msg += "\n" + avaliar_chegada(self.gasto(), self._otimo)
        return ok, msg


def avaliar_chegada(gasto, otimo):
    if gasto == otimo:
        return (f"Você gastou {gasto} de energia: a MENOR possível, igual à do Dijkstra. "
                "Rota ótima!")
    return (f"Você gastou {gasto} de energia. O Dijkstra chega gastando {otimo}. "
            "Dá para economizar: veja a comparação.")
