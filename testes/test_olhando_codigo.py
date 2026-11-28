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
