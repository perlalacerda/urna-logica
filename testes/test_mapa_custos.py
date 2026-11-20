"""
Testes da aula 11 (algoritmos gulosos): heap de mínimo (aula 08), Dijkstra,
guloso ingênuo e o desafio extra "Mapa com Custos".

    python -m unittest -v testes.test_mapa_custos
"""

import random
import unittest

from estruturas.grafo import Grafo
from estruturas.heap import HeapMinimo
from algoritmos.dijkstra import dijkstra, dijkstra_estados, guloso_ingenuo, relaxa, INFINITO
from algoritmos.solver import bfs
from jogo.fase3 import ProblemaMapa, construir_mapa, mover, estado_inicial
from jogo.mapa_custos import (FaseMapaCustos, comparar, dijkstra_grafo_puro, custo_do_caminho,
                              problema_custos, ENERGIA_CUSTOS)


def caminho_locais(r):
    return [e[0] for _, e in r.caminho]


class TestHeap(unittest.TestCase):
    def test_heap_vazio(self):
        self.assertEqual(HeapMinimo().extrair_minimo(), (False, None, None))

    def test_extrai_sempre_o_menor(self):
        random.seed(7)
        valores = [random.randint(0, 50) for _ in range(40)]
        h = HeapMinimo()
        for i, v in enumerate(valores):
            h.inserir(f"x{i}", v)
            self.assertTrue(h.eh_heap())
        saida = []
        while not h.esta_vazio():
            ok, _, p = h.extrair_minimo()
            self.assertTrue(ok)
            self.assertTrue(h.eh_heap())
            saida.append(p)
        self.assertEqual(saida, sorted(valores))        # é um heap sort

    def test_pai_e_filhos_no_vetor(self):
        """Slide 29: pai de k = k//2; filhos 2k e 2k+1."""
        h = HeapMinimo()
        for v in (16, 14, 10, 8, 7, 9, 3, 2, 4, 1):
            h.inserir(v, v)
        vet = [None] + h.vetor()
        for k in range(2, len(vet)):
            self.assertLessEqual(vet[k // 2], vet[k])
        self.assertEqual(vet[1], 1)

    def test_diminuir_chave_sobe(self):
        h = HeapMinimo()
        for nome, p in (("a", 5), ("b", 9), ("c", 7)):
            h.inserir(nome, p)
        h.diminuir_chave("b", 1)
        self.assertTrue(h.eh_heap())
        self.assertEqual(h.extrair_minimo(), (True, "b", 1))

    def test_empate_respeita_ordem_de_chegada(self):
        h = HeapMinimo()
        for nome in "xyz":
            h.inserir(nome, 3)
        self.assertEqual([h.extrair_minimo()[1] for _ in range(3)], ["x", "y", "z"])


class TestDijkstraDaAula(unittest.TestCase):
    def test_relaxa_exemplo_do_slide(self):
        """Slide do relaxamento: d[u] = 5, w = 2, d[v] = 9  ->  7."""
        d, pi = {"u": 5, "v": 9}, {"u": None, "v": None}
        self.assertTrue(relaxa("u", "v", 2, d, pi))
        self.assertEqual((d["v"], pi["v"]), (7, "u"))
        self.assertFalse(relaxa("u", "v", 2, d, pi))   # não melhora de novo

    def test_exemplo_da_aula(self):
        """Exemplo orientado da aula 11 (slides 28-30, figuras a-f): d final s0 t8 x9 y5 z7."""
        G = Grafo(orientado=True)
        for u, v, w in [("s", "t", 10), ("s", "y", 5), ("t", "x", 1), ("t", "y", 2), ("y", "t", 3),
                        ("y", "x", 9), ("y", "z", 2), ("x", "z", 4), ("z", "x", 6), ("z", "s", 7)]:
            G.adicionar_aresta(u, v, w)
        d, pi, S, _ = dijkstra(G, "s")
        self.assertEqual(d, {"s": 0, "t": 8, "x": 9, "y": 5, "z": 7})
        self.assertEqual(S, ["s", "y", "z", "t", "x"])     # ordem de Extrai-Min dos slides
        self.assertEqual((pi["t"], pi["x"], pi["z"]), ("y", "t", "y"))

    def test_peso_negativo_recusado(self):
        with self.assertRaises(ValueError):
            Grafo().adicionar_aresta("a", "b", -1)

    def test_sem_aresta_peso_infinito(self):
        self.assertEqual(construir_mapa().peso("A", "F"), INFINITO)

    def test_sem_pesos_dijkstra_igual_bfs(self):
        """Com todos os pesos 1, Dijkstra e BFS acham o mesmo custo (generalização)."""
        P = ProblemaMapa()
        self.assertEqual(dijkstra_estados(P).custo, bfs(P).custo)


class TestMapaComCustos(unittest.TestCase):
    def setUp(self):
        self.bfs, self.guloso, self.dij = comparar()

    def test_bfs_menos_movimentos_mais_energia(self):
        self.assertEqual(caminho_locais(self.bfs), list("ACECBHDF"))
        self.assertEqual((self.bfs.numero_acoes(), self.bfs.custo), (7, 15))

    def test_dijkstra_menos_energia(self):
        self.assertEqual(caminho_locais(self.dij), list("ABCECBHDF"))
        self.assertEqual((self.dij.numero_acoes(), self.dij.custo), (8, 11))
        self.assertLess(self.dij.custo, self.bfs.custo)
        self.assertGreater(self.dij.numero_acoes(), self.bfs.numero_acoes())

    def test_dijkstra_e_o_minimo(self):
        """Confere por força bruta: nenhum estado-objetivo alcançável custa menos que 11."""
        P = problema_custos()
        melhor, pilha, vistos = None, [P.estado_inicial()], set()
        while pilha:
            e = pilha.pop()
            if e in vistos:
                continue
            vistos.add(e)
            if P.eh_objetivo(e):
                gasto = ENERGIA_CUSTOS - e[3]
                melhor = gasto if melhor is None else min(melhor, gasto)
                continue
            pilha.extend(novo for _, novo, _ in P.sucessores(e))
        self.assertEqual(melhor, self.dij.custo)

    def test_guloso_trava(self):
        self.assertFalse(self.guloso.encontrou)
        self.assertEqual(caminho_locais(self.guloso), list("ABCECBA"))

    def test_custos_batem_com_os_corredores(self):
        self.assertEqual(custo_do_caminho(caminho_locais(self.bfs)), self.bfs.custo)
        self.assertEqual(custo_do_caminho(caminho_locais(self.dij)), self.dij.custo)

    def test_dijkstra_grafo_puro_ignora_portas(self):
        d, _, _, _, caminho = dijkstra_grafo_puro()
        self.assertEqual((caminho, d["F"]), (list("ABHDF"), 7))
        e = estado_inicial(ENERGIA_CUSTOS)
        G = FaseMapaCustos().G
        ok, _, _ = mover(G, e, "B")
        ok2, _, msg = mover(G, mover(G, e, "B")[1], "H")
        self.assertTrue(ok)
        self.assertFalse(ok2)                       # a rota do grafo puro esbarra na porta H
        self.assertIn("SEQ", msg)

    def test_energia_insuficiente_para_corredor_caro(self):
        G = FaseMapaCustos().G
        ok, _, msg = mover(G, ("A", (), (), 5), "C")
        self.assertFalse(ok)
        self.assertIn("consome 6", msg)

    def test_jogador_rota_otima(self):
        f = FaseMapaCustos()
        for v in "BCECBHDF":
            ok, msg = f.ir_para(v)
            self.assertTrue(ok, msg)
        self.assertTrue(f.venceu())
        self.assertEqual(f.gasto(), 11)
        self.assertIn("Rota ótima", msg)

    def test_jogador_rota_da_bfs(self):
        f = FaseMapaCustos()
        for v in "CECBHDF":
            ok, msg = f.ir_para(v)
            self.assertTrue(ok, msg)
        self.assertEqual(f.gasto(), 15)
        self.assertIn("gastando 11", msg)
        self.assertNotIn("Selo 3", msg)

    def test_fase3_original_inalterada(self):
        """O mapa padrão continua custando 1 por movimento."""
        r = bfs(ProblemaMapa())
        self.assertEqual((r.numero_acoes(), r.custo), (7, 7))


if __name__ == "__main__":
    unittest.main()
