"""
Testes do grafo, da BFS/DFS e do solver (seção 15: Grafo, BFS/DFS, Estados,
Regras do jogo, Integração).

    python -m unittest -v testes.test_grafo_busca
"""

import unittest

from estruturas.grafo import Grafo
from algoritmos.busca_grafo import bfs, dfs, caminho, INFINITO
from algoritmos.solver import bfs as solver_bfs, dfs_recursiva, dfs_pilha
from jogo.fase2 import Fase2, ProblemaTriagem
from jogo.fase3 import (Fase3, ProblemaMapa, construir_mapa, mover, estado_inicial,
                        chave_estado, regra_porta)


def grafo_da_aula():
    """Exemplo de BFS da aula 09 (slides 60-70), não orientado."""
    G = Grafo()
    for u, v in [("r", "s"), ("r", "v"), ("s", "w"), ("w", "t"), ("w", "x"),
                 ("t", "x"), ("t", "u"), ("x", "y"), ("u", "y")]:
        G.adicionar_aresta(u, v)
    return G


class TestGrafo(unittest.TestCase):
    def test_vizinhos_repetidos_sao_ignorados(self):
        G = Grafo()
        G.adicionar_aresta("A", "B")
        G.adicionar_aresta("A", "B")
        G.adicionar_aresta("B", "A")
        self.assertEqual(G.vizinhos("A"), ["B"])
        self.assertEqual(G.numero_arestas(), 1)

    def test_vizinhos_em_ordem_alfabetica(self):
        G = Grafo()
        for v in ["D", "B", "C"]:
            G.adicionar_aresta("A", v)
        self.assertEqual(G.vizinhos("A"), ["B", "C", "D"])

    def test_orientado(self):
        G = Grafo(orientado=True)
        G.adicionar_aresta("A", "B")
        self.assertTrue(G.existe_aresta("A", "B"))
        self.assertFalse(G.existe_aresta("B", "A"))

    def test_vertice_isolado_e_destino_inalcancavel(self):
        G = grafo_da_aula()
        G.adicionar_vertice("z")                  # isolado
        d, pi, ordem, _ = bfs(G, "s")
        self.assertEqual(d["z"], INFINITO)
        self.assertNotIn("z", ordem)
        self.assertEqual(caminho(pi, "s", "z"), [])

    def test_mapa_do_jogo_atende_o_enunciado(self):
        """Seção 7.1: pelo menos 8 vértices e 10 conexões, com bifurcação."""
        G = construir_mapa()
        self.assertGreaterEqual(len(G.vertices()), 8)
        self.assertGreaterEqual(G.numero_arestas(), 10)
        self.assertGreaterEqual(G.grau("A"), 2)   # bifurcação logo no início


class TestBFSDFSdaAula(unittest.TestCase):
    def test_bfs_distancias_da_aula(self):
        d, pi, ordem, maior_fila = bfs(grafo_da_aula(), "s")
        esperado = {"s": 0, "r": 1, "w": 1, "v": 2, "t": 2, "x": 2, "u": 3, "y": 3}
        self.assertEqual(d, esperado)
        self.assertEqual(ordem, ["s", "r", "w", "v", "t", "x", "u", "y"])
        self.assertEqual(caminho(pi, "s", "y"), ["s", "w", "x", "y"])

    def test_bfs_menor_numero_de_arestas_com_ciclos(self):
        """Caminhos alternativos e ciclos: a BFS acha o de menos arestas."""
        G = construir_mapa()
        d, pi, _, _ = bfs(G, "A")
        self.assertEqual(caminho(pi, "A", "F"), ["A", "C", "G", "F"])
        self.assertEqual(d["F"], 3)

    def test_dfs_exemplo_do_slide(self):
        """Aula 09, slides 29-52 (grafo orientado): d|f do slide 52 e floresta com 2 árvores."""
        G = Grafo(orientado=True)
        for u, v in [("s", "r"), ("s", "t"), ("s", "w"), ("r", "v"), ("r", "w"), ("v", "s"), ("t", "w"),
                     ("t", "x"), ("x", "w"), ("w", "v"), ("u", "t"), ("u", "x"), ("u", "y"), ("y", "w")]:
            G.adicionar_aresta(u, v)
        d, f, pi, _ = dfs(G, ["s", "r", "t", "u", "v", "w", "x", "y"])
        esperado = {"s": (1, 12), "r": (2, 7), "v": (3, 4), "w": (5, 6), "t": (8, 11), "x": (9, 10), "u": (13, 16), "y": (14, 15)}
        self.assertEqual({v: (d[v], f[v]) for v in esperado}, esperado)
        self.assertEqual([v for v in pi if pi[v] is None], ["s", "u"])     # duas raízes = duas árvores

    def test_dfs_intervalos_aninhados(self):
        """Teorema dos parênteses: intervalos [d, f] são disjuntos ou um contém o outro; π[v] = u => [d[v], f[v]] dentro de [d[u], f[u]]."""
        d, f, pi, _ = dfs(grafo_da_aula())
        for u in d:
            for v in d:
                if u != v:
                    disjuntos = f[u] < d[v] or f[v] < d[u]
                    aninhados = (d[u] < d[v] < f[v] < f[u]) or (d[v] < d[u] < f[u] < f[v])
                    self.assertTrue(disjuntos or aninhados, (u, v))
            if pi[u] is not None:
                self.assertTrue(d[pi[u]] < d[u] < f[u] < f[pi[u]])

    def test_dfs_tempos(self):
        d, f, pi, ordem = dfs(grafo_da_aula())
        for u in d:
            self.assertLess(d[u], f[u])           # descoberto antes de finalizado
        self.assertEqual(sorted(list(d.values()) + list(f.values())), list(range(1, 17)))
        self.assertEqual(ordem[0], "r")           # começa pelo 1º vértice em ordem alfabética
        self.assertEqual(len(ordem), 8)           # grafo conexo: uma só árvore


class TestRegrasFase3(unittest.TestCase):
    def setUp(self):
        self.G = construir_mapa()

    def test_mesma_posicao_pistas_diferentes_sao_estados_diferentes(self):
        """Enigma 8.2: mesmo vértice, com e sem pista -> chaves diferentes."""
        sem = ("D", (), ("H",), 5)
        com = ("D", ("AUT", "SEQ"), ("H",), 5)
        self.assertNotEqual(chave_estado(sem), chave_estado(com))
        self.assertFalse(mover(self.G, sem, "F")[0])   # permitem ações diferentes
        self.assertTrue(mover(self.G, com, "F")[0])

    def test_cenario_1_caminho_mais_curto_e_invalido(self):
        """A-C-G-F tem 3 arestas, mas viola R4 (F exige AUT)."""
        e = estado_inicial()
        for v in ["C", "G"]:
            ok, e, _ = mover(self.G, e, v)
            self.assertTrue(ok)
        ok, novo, msg = mover(self.G, e, "F")
        self.assertFalse(ok)
        self.assertIsNone(novo)
        self.assertIn("AUT", msg)

    def test_cenario_2_porta_oeste_sem_sequencia(self):
        """A-B-H viola R3 (H exige SEQ)."""
        ok, e, _ = mover(self.G, estado_inicial(), "B")
        ok, novo, msg = mover(self.G, e, "H")
        self.assertFalse(ok)
        self.assertIn("SEQ", msg)

    def test_sem_conexao(self):
        self.assertFalse(mover(self.G, estado_inicial(), "F")[0])

    def test_energia_insuficiente(self):
        self.assertFalse(mover(self.G, ("A", (), (), 0), "B")[0])

    def test_pista_coletada(self):
        ok, e, msg = mover(self.G, ("C", (), (), 5), "E")
        self.assertEqual(e, ("E", ("SEQ",), (), 4))
        self.assertIn("Pista coletada", msg)

    def test_regra_porta(self):
        self.assertTrue(regra_porta("H", ("SEQ",))[0])
        self.assertFalse(regra_porta("H", ())[0])
        self.assertTrue(regra_porta("B", ())[0])     # B não tem porta


class TestSolver(unittest.TestCase):
    ROTA_ESPERADA = ["A", "C", "E", "C", "B", "H", "D", "F"]

    def test_bfs_mapa_menor_numero_de_acoes(self):
        r = solver_bfs(ProblemaMapa())
        self.assertTrue(r.encontrou)
        self.assertEqual([e[0] for _, e in r.caminho], self.ROTA_ESPERADA)
        self.assertEqual(r.custo, 7)
        self.assertGreater(r.repetidos, 0)           # a AVL evitou reexpandir estados

    def test_todas_as_estrategias_respeitam_as_regras(self):
        G = construir_mapa()
        for alg in (solver_bfs, dfs_recursiva, dfs_pilha):
            with self.subTest(algoritmo=alg.__name__):
                r = alg(ProblemaMapa())
                self.assertTrue(r.encontrou)
                self.assertEqual(r.caminho[-1][1][0], "F")
                self.assertIn("AUT", r.caminho[-1][1][1])
                # refaz o caminho com as regras do jogador: cada passo tem de ser válido
                e = r.caminho[0][1]
                for _, prox in r.caminho[1:]:
                    ok, e, _ = mover(G, e, prox[0])
                    self.assertTrue(ok)
                    self.assertEqual(e, prox)

    def test_bfs_nunca_pior_que_dfs_em_numero_de_acoes(self):
        b = solver_bfs(ProblemaMapa())
        for alg in (dfs_recursiva, dfs_pilha):
            self.assertLessEqual(b.numero_acoes(), alg(ProblemaMapa()).numero_acoes())

    def test_sem_solucao_por_energia(self):
        for alg in (solver_bfs, dfs_recursiva, dfs_pilha):
            r = alg(ProblemaMapa(energia=6))
            self.assertFalse(r.encontrou)

    def test_estados_repetidos_nao_sao_expandidos(self):
        r = solver_bfs(ProblemaMapa())
        chaves = [chave_estado(e) for e in r.ordem]
        self.assertEqual(len(chaves), len(set(chaves)))   # nenhuma chave expandida 2x

    def test_dominancia_de_energia(self):
        """Com energia 7 ou 8 há solução, mas só se a mesma chave puder ser revisitada com MAIS energia."""
        for energia in (7, 8):
            for alg in (solver_bfs, dfs_recursiva, dfs_pilha):
                with self.subTest(energia=energia, algoritmo=alg.__name__):
                    self.assertTrue(alg(ProblemaMapa(energia=energia)).encontrou)

    def test_solver_resolve_fase2(self):
        for alg in (solver_bfs, dfs_recursiva, dfs_pilha):
            with self.subTest(algoritmo=alg.__name__):
                r = alg(ProblemaTriagem())
                self.assertTrue(r.encontrou)
                f = Fase2()                                # refaz no jogo manual
                for acao, _ in r.caminho[1:]:
                    self.assertTrue(f.executar(acao)[0])
                self.assertTrue(f.venceu())


class TestIntegracaoFase3(unittest.TestCase):
    def test_manual_e_solver_chegam_ao_mesmo_estado_final(self):
        f = Fase3()
        for v in TestSolver.ROTA_ESPERADA[1:]:
            ok, msg = f.ir_para(v)
            self.assertTrue(ok, msg)
        self.assertTrue(f.venceu())
        r = solver_bfs(ProblemaMapa())
        self.assertEqual(f.estado, r.caminho[-1][1])

    def test_jogada_invalida_nao_altera_estado(self):
        f = Fase3()
        antes = f.estado
        self.assertFalse(f.ir_para("F")[0])
        self.assertFalse(f.ir_para("Z")[0])
        self.assertEqual(f.estado, antes)

    def test_aviso_de_estado_ja_explorado(self):
        f = Fase3()
        f.ir_para("B")
        f.ir_para("A")
        ok, msg = f.ir_para("B")                 # B, sem pistas, agora com menos energia
        self.assertTrue(ok)
        self.assertIn("já explorado", msg)

    def test_desfazer_e_reiniciar(self):
        f = Fase3()
        f.ir_para("C")
        f.ir_para("E")
        self.assertTrue(f.desfazer()[0])
        self.assertEqual(f.estado, ("C", (), (), 9))
        f.reiniciar()
        self.assertEqual(f.estado, estado_inicial())
        self.assertFalse(f.desfazer()[0])


if __name__ == "__main__":
    unittest.main()
