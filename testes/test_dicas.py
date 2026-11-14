"""
Testes das dicas: a dica das Fases 2 e 3 vem do solver (BFS) a partir da
situação atual, então segui-la sempre leva à vitória.
    python -m unittest -v testes.test_dicas
"""

import re
import unittest

from jogo.fase2 import Fase2
from jogo.fase3 import Fase3
from jogo import dicas
from interface.terminal import ler_opcao, _sem_acento


class TestDicas(unittest.TestCase):
    def test_seguir_as_dicas_vence_a_fase2(self):
        f = Fase2()
        nomes = {"1": "aceitar", "2": "guardar", "3": "arquivar", "4": "liberar"}
        for _ in range(10):
            if f.venceu():
                break
            numero = re.search(r"sugere: (\d)", dicas.dica_fase2(f)).group(1)
            self.assertTrue(f.executar(nomes[numero])[0])
        self.assertTrue(f.venceu())

    def test_dica_fase2_depois_de_erro_ainda_leva_ao_fim(self):
        f = Fase2()
        f.executar("guardar"); f.executar("aceitar"); f.executar("arquivar")
        self.assertIn("sugere", dicas.dica_fase2(f))

    def test_seguir_as_dicas_vence_a_fase3(self):
        f = Fase3()
        for _ in range(12):
            if f.venceu():
                break
            letra = re.search(r"ir para ([A-I]) ", dicas.dica_fase3(f)).group(1)
            self.assertTrue(f.ir_para(letra)[0])
        self.assertTrue(f.venceu())
        self.assertEqual(f.trilha, ["A", "C", "E", "C", "B", "H", "D", "F"])

    def test_dica_fase3_sem_saida(self):
        f = Fase3(energia=2)
        f.ir_para("B")
        self.assertIn("Desfaça", dicas.dica_fase3(f))

    def test_orientacao_muda_com_a_situacao(self):
        f = Fase3()
        self.assertIn("SEQ", dicas.orientacao_fase3(f))
        for v in ["C", "E"]:
            f.ir_para(v)
        self.assertIn("AUT", dicas.orientacao_fase3(f))

    def test_dica_nao_altera_o_jogo(self):
        f2, f3 = Fase2(), Fase3()
        e2, e3 = f2.estado(), f3.estado
        dicas.dica_fase2(f2); dicas.dica_fase3(f3)
        self.assertEqual((f2.estado(), f3.estado), (e2, e3))


class TestEntrada(unittest.TestCase):
    def test_palavras_e_acentos(self):
        import builtins
        respostas = iter(["xyz", "INSTRUÇÕES"])
        original = builtins.input
        builtins.input = lambda _="": next(respostas)
        try:
            self.assertEqual(ler_opcao(["1", "3"], apelidos={"instrucoes": "3"}), "3")
        finally:
            builtins.input = original
        self.assertEqual(_sem_acento("não"), "nao")


if __name__ == "__main__":
    unittest.main()
