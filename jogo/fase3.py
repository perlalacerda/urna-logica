"""
FASE 3 — O Mapa das Seções                           (seção 7 do enunciado)

Conceitos: grafo (lista de adjacência), estado, BFS, DFS, árvore de busca.

MAPA (grafo NÃO orientado: os corredores valem nos dois sentidos)

    Vértice  Local                  Vizinhos      Observação
    A        Central de Auditoria   B, C          início (bifurcação)
    B        Arquivo Norte          A, C, H, I
    C        Arquivo Sul            A, B, E, G
    D        Unidade Leste          F, H          guarda a pista AUT
    E        Unidade Oeste          C             guarda a pista SEQ (beco: só se sai por C)
    F        Centro de Validação    D, G          destino; porta exige AUT
    G        Galeria de Lacres      C, F, I       rota alternativa até F
    H        Arquivo Oeste          B, D          porta exige SEQ
    I        Sala de Cópias         B, G

    Arestas (11): A-B, A-C, B-C, B-H, B-I, C-E, C-G, D-F, D-H, F-G, G-I
    Vértices (9): A B C D E F G H I

REGRAS FORMAIS (o item 7.5 transformado em condições verificáveis)
    R1 Adjacência : mover de u para v só se {u, v} é aresta do grafo.
    R2 Energia    : mover exige energia >= 1 e consome 1 unidade.
                    (No mapa com custos, jogo/mapa_custos.py, consome w(u, v).)
    R3 Porta Oeste: entrar em H (Arquivo Oeste) exige a pista SEQ.
    R4 Porta Final: entrar em F (Centro de Validação) exige a pista AUT.
                    => a rota passa pelo ponto de autenticação ANTES de F.
    R5 Pistas     : ao chegar em E, ganha SEQ; ao chegar em D, ganha AUT.
    Objetivo      : estar em F.

ESTADO = (posição, pistas_coletadas, portas_liberadas, energia)
    Dois estados na MESMA posição são diferentes se as pistas forem
    diferentes — ex.: em C sem pistas (início) e em C com SEQ (na volta de E).

O enigma: o caminho mais curto em número de conexões, A-C-G-F (3 arestas),
é INVÁLIDO: chega a F sem AUT. A rota válida precisa buscar SEQ em E,
voltar por C, atravessar a porta de H e pegar AUT em D:
    A -> C -> E -> C -> B -> H -> D -> F   (7 movimentos)
O solver encontra isso sozinho, a partir das regras — não há rota no código.
"""

from estruturas.grafo import Grafo
from estruturas.pilha import Pilha
from estruturas.avl import ArvoreAVL
from algoritmos.busca_grafo import bfs as bfs_grafo, caminho as caminho_grafo

LOCAIS = {
    "A": "Central de Auditoria",
    "B": "Arquivo Norte",
    "C": "Arquivo Sul",
    "D": "Unidade Leste",
    "E": "Unidade Oeste",
    "F": "Centro de Validação",
    "G": "Galeria de Lacres",
    "H": "Arquivo Oeste",
    "I": "Sala de Cópias",
}
ARESTAS = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "H"), ("B", "I"), ("C", "E"),
           ("C", "G"), ("D", "F"), ("D", "H"), ("F", "G"), ("G", "I")]
PISTAS = {"E": "SEQ", "D": "AUT"}                  # vértice -> pista que ele guarda
PORTAS = {"H": "SEQ", "F": "AUT"}                  # vértice -> pista exigida para entrar
NOMES_PISTAS = {"SEQ": "pista de sequência", "AUT": "pista de autenticação"}
INICIO, DESTINO = "A", "F"
ENERGIA_PADRAO = 10


def construir_mapa(arestas=ARESTAS, locais=LOCAIS):
    G = Grafo(orientado=False)
    for v, nome in locais.items():
        G.adicionar_vertice(v, nome)
    for u, v in arestas:
        G.adicionar_aresta(u, v)
    return G


# ======================================================== REGRAS (funções)
def regra_adjacencia(G, u, v):
    if G.existe_aresta(u, v):
        return True, ""
    return False, f"Não há conexão entre {u} ({G.nomes[u]}) e {v} ({G.nomes.get(v, '?')})."


def regra_energia(energia, custo=1):
    """R2. No mapa com custos (variante da aula 11), o movimento consome w(u, v)."""
    if energia >= custo:
        return True, ""
    if custo == 1:
        return False, "Energia insuficiente: cada movimento consome 1 unidade."
    return False, f"Energia insuficiente: este corredor consome {custo} e restam {energia}."


def regra_porta(v, pistas, portas=PORTAS):
    exigida = portas.get(v)
    if exigida is None or exigida in pistas:
        return True, ""
    return False, (f"Porta bloqueada: entrar em {v} ({LOCAIS.get(v, v) if v in LOCAIS else 'local ' + v}) exige a "
                   f"{NOMES_PISTAS.get(exigida, exigida)} ({exigida}).")


def estado_inicial(energia=ENERGIA_PADRAO, inicio=INICIO):
    """(posição, pistas, portas_liberadas, energia) — tuplas ordenadas, para comparar."""
    return (inicio, (), (), energia)


def mover(G, estado, v, portas=PORTAS, pistas_mapa=PISTAS):
    """
    Aplica as regras R1-R5. Devolve (ok, novo_estado_ou_None, mensagem).
    É usada TANTO pelo jogador QUANTO pelo solver.
    """
    pos, pistas, abertas, energia = estado
    ok, motivo = regra_adjacencia(G, pos, v)
    if not ok:
        return False, None, motivo
    custo = G.peso(pos, v)                     # 1 no mapa padrão; w(u, v) no mapa com custos
    for ok, motivo in (regra_energia(energia, custo), regra_porta(v, pistas, portas)):
        if not ok:
            return False, None, motivo
    novas_pistas, novas_portas = set(pistas), set(abertas)
    msg = f"Você foi de {pos} ({G.nomes[pos]}) para {v} ({G.nomes[v]})."
    if v in portas:
        if v not in novas_portas:
            msg += f" Porta de {v} liberada."
        novas_portas.add(v)
    if v in pistas_mapa and pistas_mapa[v] not in novas_pistas:
        novas_pistas.add(pistas_mapa[v])
        msg += f" Pista coletada: {NOMES_PISTAS[pistas_mapa[v]]} ({pistas_mapa[v]})."
    if custo != 1:
        msg += f" Gastou {custo} de energia."
    novo = (v, tuple(sorted(novas_pistas)), tuple(sorted(novas_portas)), energia - custo)
    return True, novo, msg


def chave_estado(estado):
    """
    Chave usada na AVL de visitados: (posição, pistas, portas, energia).
    É o estado INTEIRO, como pede o enunciado (8.1: "a chave deve representar
    todos os elementos que tornam um estado distinto"; Etapa 7: "posição igual
    não significa estado igual quando pistas, portas ou energia diferem").
    Pistas e portas já vêm ordenadas (tuplas), então a chave é canônica.
    """
    return estado[0], estado[1], estado[2], estado[3]


def configuracao(estado):
    """
    (posição, pistas, portas): o estado SEM a energia. Usada só pela regra de
    dominância, a melhoria opcional do solver (ver algoritmos/solver.py), e
    pelo Dijkstra, em que a energia restante é a própria distância (E - d).
    """
    return estado[0], estado[1], estado[2]


def rotulo(estado):
    pos, pistas, portas, energia = estado
    return f"{pos} pistas={{{','.join(pistas)}}} portas={{{','.join(portas)}}} energia={energia}"


# ======================================================== problema p/ o solver
class ProblemaMapa:
    """Adaptador da Fase 3 para o solver (mesmas regras do jogador)."""

    def __init__(self, G=None, energia=ENERGIA_PADRAO, destino=DESTINO, inicio=INICIO,
                 pistas=PISTAS, portas=PORTAS):
        self.G = G or construir_mapa()
        self.energia = energia
        self.destino = destino
        self.inicio = inicio
        self.pistas = pistas
        self.portas = portas

    def estado_inicial(self):
        return estado_inicial(self.energia, self.inicio)

    def sucessores(self, estado):
        res = []
        for v in self.G.vizinhos(estado[0]):
            ok, novo, _ = mover(self.G, estado, v, self.portas, self.pistas)
            if ok:
                res.append((f"ir para {v}", novo, self.G.peso(estado[0], v)))
        return res

    def eh_objetivo(self, estado):
        return estado[0] == self.destino

    def chave(self, estado):
        return chave_estado(estado)

    def configuracao(self, estado):
        return configuracao(estado)

    def recurso(self, estado):
        return estado[3]


# ======================================================== a fase (modo manual)
class Fase3:
    NOME = "Fase 3 — O Mapa das Seções"
    ABERTURA = ("As evidências estão organizadas, mas a trilha entre os locais foi fragmentada.\n"
                "Há caminhos alternativos, conexões interrompidas e passagens que dependem\n"
                "de pistas já coletadas. Reconstrua a rota sem se perder no mapa.")

    def __init__(self, energia=ENERGIA_PADRAO):
        self.G = construir_mapa()
        self.energia_inicial = energia
        self.reiniciar()

    def reiniciar(self):
        self.estado = estado_inicial(self.energia_inicial)
        self.historico = Pilha()            # para desfazer movimentos
        self.visitados = ArvoreAVL()        # configurações já vistas pelo jogador (só para o aviso)
        self.visitados.inserir(configuracao(self.estado), self.estado[3])
        self.trilha = [INICIO]

    def venceu(self):
        return self.estado[0] == DESTINO

    def ir_para(self, v):
        v = v.strip().upper()
        ok, novo, msg = mover(self.G, self.estado, v)
        if not ok:
            return False, "Movimento recusado: " + msg       # nada muda
        self.historico.push(self.estado)
        self.estado = novo
        self.trilha.append(v)
        achou, energia_antes, _ = self.visitados.buscar(configuracao(novo))
        if achou and novo[3] <= energia_antes:
            msg += ("\nAviso: você já esteve aqui com as mesmas pistas e portas "
                    "(e mais energia). Esse desvio não abre nada de novo.")
        elif achou:
            self.visitados.atualizar_valor(configuracao(novo), novo[3])
        else:
            self.visitados.inserir(configuracao(novo), novo[3])
        if self.venceu():
            msg += "\nVocê chegou ao Centro de Validação com a autenticação. Selo 3 conquistado!"
        elif novo[3] == 0:
            msg += "\nSua energia acabou. Desfaça movimentos ou reinicie a fase."
        return True, msg

    def desfazer(self):
        ok, anterior = self.historico.pop()
        if not ok:
            return False, "Não há movimento para desfazer."
        self.estado = anterior
        self.trilha.pop()
        return True, f"Movimento desfeito. Você voltou para {anterior[0]}."

    def menor_caminho_ignorando_portas(self):
        """BFS da aula 09 no grafo puro (sem pistas nem portas)."""
        d, pi, ordem, _ = bfs_grafo(self.G, INICIO)
        return caminho_grafo(pi, INICIO, DESTINO), ordem
