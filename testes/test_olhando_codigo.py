"""'Olhando o código': a gravação vem da execução real e bate com o algoritmo."""
import unittest

from algoritmos.ordenacao import ordenar
from interface.olhando_codigo import dados_motor_fase1
from jogo.fase1 import Fase1
from jogo.registros import CRITERIOS


class TestOlhandoCodigo(unittest.TestCase):
    def setUp(self):
        self.reg = Fase1().registros
        self.chave = CRITERIOS["auditoria"]
        self.M = dados_motor_fase1(self.reg, self.chave)

    def test_resultado_e_contadores_iguais_aos_do_algoritmo(self):
        for alg, G in self.M["algoritmos"].items():
            A = list(self.reg)[:8]
            c = ordenar(A, alg, self.chave)
            fim = G["passos"][-1]
            self.assertEqual(fim["vetor"], [r.id_registro for r in A], alg)        # termina ordenado
            self.assertEqual((fim["comp"], fim["mov"]), (c.comparacoes, c.movimentacoes), alg)

    def test_cada_linha_acesa_existe_no_codigo_mostrado(self):
        fonte = open("algoritmos/ordenacao.py", encoding="utf-8").read().split("\n")
        for alg, G in self.M["algoritmos"].items():
            mostradas = {n for n, _ in G["codigo"] if n}
            for p in G["passos"][:-1]:
                self.assertIn(p["linha"], mostradas, (alg, p["linha"]))
                self.assertEqual(fonte[p["linha"] - 1].rstrip(), dict(G["codigo"])[p["linha"]].rstrip())
                self.assertTrue(p["did"] and p["tec"], (alg, p["linha"]))

    def test_contadores_nunca_diminuem(self):
        for G in self.M["algoritmos"].values():
            comps = [p["comp"] for p in G["passos"]]
            self.assertEqual(comps, sorted(comps))


if __name__ == "__main__":
    unittest.main()


class TestOlhandoCodigoBuscaEAVL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface.olhando_codigo import dados_motor_fase3, dados_motor_fase4
        cls.f3 = dados_motor_fase3()["algoritmos"]
        cls.f4 = dados_motor_fase4()["algoritmos"]

    def test_linhas_acesas_existem_no_arquivo(self):
        for G in list(self.f3.values()) + list(self.f4.values()):
            fonte = open(G["arquivo"], encoding="utf-8").read().split("\n")
            mostradas = dict((n, t) for n, t in G["codigo"] if n)
            for p in G["passos"]:
                if p["linha"] is None:
                    continue
                self.assertIn(p["linha"], mostradas, (G["arquivo"], p["linha"]))
                self.assertEqual(fonte[p["linha"] - 1].rstrip(), mostradas[p["linha"]].rstrip())
                self.assertTrue(p["did"], (G["arquivo"], p["linha"]))

    def test_buscas_terminam_com_o_resultado_do_solver(self):
        self.assertIn("7 passos, A → C → E → C → B → H → D → F", self.f3["bfs"]["passos"][-1]["did"])
        self.assertIn("10 passos", self.f3["dfs"]["passos"][-1]["did"])
        fim = self.f3["bfs_aula"]["passos"][-1]["mapa"]["d"]
        self.assertEqual((fim["A"], fim["C"], fim["F"]), (0, 1, 3))     # distâncias em corredores

    def test_avl_rotacoes_da_aula(self):
        fim = self.f4["avl"]["passos"][-1]
        self.assertEqual(fim["tec"], "rotações: RD em 70, RE em 70, RED em 40, RDE em 40")
        self.assertEqual(fim["cont"], [9, 4])
