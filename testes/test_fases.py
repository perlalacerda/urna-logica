"""
Testes das regras do jogo — Fases 1 e 2 (seção 15: "Regras do jogo").

    python -m unittest -v testes.test_fases

Casos: jogada válida, jogada inválida (sem alterar nada), desfazer,
reinício, conclusão, seed reproduzível.
"""

import unittest

from jogo.fase1 import Fase1, CHAVE_AUDITORIA
from jogo.fase2 import Fase2, regra_aceitar, regra_guardar, regra_arquivar, regra_liberar
from estruturas.pilha import Pilha
from algoritmos.ordenacao import primeiro_fora_de_ordem


class TestFase1(unittest.TestCase):
    def test_lote_tem_horarios_repetidos_em_zonas_diferentes(self):
        """Pré-condição do enigma 5.3."""
        f = Fase1()
        zonas_por_horario = {}
        for r in f.registros:
            zonas_por_horario.setdefault(r.timestamp, set()).add(r.zona)
        self.assertTrue(any(len(z) > 1 for z in zonas_por_horario.values()))

    def test_criterio_errado_recusa_e_aponta_erro(self):
        f = Fase1()
        res = f.ordenar("merge", "horario")
        self.assertFalse(res["aceito"])
        self.assertGreaterEqual(res["posicao_erro"], 0)
        self.assertFalse(f.selo)

    def test_criterio_certo_ganha_selo_com_qualquer_algoritmo(self):
        for alg in ("bubble", "merge", "quick"):
            with self.subTest(algoritmo=alg):
                f = Fase1()
                res = f.ordenar(alg, "auditoria")
                self.assertTrue(res["aceito"])
                self.assertTrue(f.selo)
                self.assertEqual(primeiro_fora_de_ordem(f.registros, CHAVE_AUDITORIA), -1)

    def test_entrada_invalida_nao_altera_lote(self):
        f = Fase1()
        antes = [r.id_registro for r in f.registros]
        self.assertFalse(f.ordenar("heap", "auditoria")["ok"])
        self.assertFalse(f.ordenar("merge", "cor")["ok"])
        self.assertEqual([r.id_registro for r in f.registros], antes)

    def test_reiniciar_volta_ao_mesmo_lote(self):
        f = Fase1()
        antes = [r.id_registro for r in f.registros]
        f.ordenar("quick", "auditoria")
        f.reiniciar()
        self.assertEqual([r.id_registro for r in f.registros], antes)
        self.assertFalse(f.selo)

    def test_comparar_nao_altera_lote_do_jogador(self):
        f = Fase1()
        antes = [r.id_registro for r in f.registros]
        linhas = f.comparar_algoritmos(tamanhos=(10, 50))
        self.assertEqual(len(linhas), 6)        # 2 tamanhos x 3 algoritmos
        self.assertEqual([r.id_registro for r in f.registros], antes)


class TestRegrasFase2(unittest.TestCase):
    ALVO = ("E2", "E4", "E1", "E6")

    def test_regra_aceitar(self):
        self.assertTrue(regra_aceitar((), self.ALVO, "E2")[0])
        self.assertFalse(regra_aceitar((), self.ALVO, "E1")[0])
        self.assertFalse(regra_aceitar((), self.ALVO, "E3")[0])

    def test_regra_guardar(self):
        p = Pilha()
        self.assertTrue(regra_guardar(p, self.ALVO, "E1")[0])
        self.assertFalse(regra_guardar(p, self.ALVO, "E3")[0])     # não faz parte
        p.push("E1")
        self.assertTrue(regra_guardar(p, self.ALVO, "E4")[0])      # E4 sai antes de E1
        self.assertFalse(regra_guardar(p, self.ALVO, "E6")[0])     # E6 enterraria E1

    def test_regra_arquivar(self):
        self.assertTrue(regra_arquivar(self.ALVO, "E3")[0])
        self.assertFalse(regra_arquivar(self.ALVO, "E2")[0])

    def test_regra_liberar(self):
        self.assertTrue(regra_liberar(("E2", "E4"), self.ALVO, "E1")[0])
        self.assertFalse(regra_liberar(("E2",), self.ALVO, "E1")[0])


class TestFase2(unittest.TestCase):
    SOLUCAO = ["guardar", "aceitar", "arquivar", "aceitar", "liberar", "arquivar", "aceitar"]

    def test_solucao_completa(self):
        f = Fase2()
        for a in self.SOLUCAO:
            ok, msg = f.executar(a)
            self.assertTrue(ok, msg)
        self.assertTrue(f.venceu())
        self.assertEqual(f.custodia.percorrer(), ["E2", "E4", "E1", "E6"])
        self.assertEqual(f.arquivo, ["E3", "E5"])

    def test_jogada_invalida_nao_altera_estado(self):
        f = Fase2()
        antes = f.estado()
        ok, msg = f.executar("aceitar")             # E1 não é o próximo esperado
        self.assertFalse(ok)
        self.assertIn("recusado", msg)
        self.assertEqual(f.estado(), antes)
        self.assertFalse(f.executar("liberar")[0])  # pilha vazia
        self.assertFalse(f.executar("voar")[0])     # ação inexistente
        self.assertEqual(f.estado(), antes)

    def test_desfazer_lifo(self):
        f = Fase2()
        e0 = f.estado()
        f.executar("guardar")
        e1 = f.estado()
        f.executar("aceitar")
        self.assertTrue(f.desfazer()[0])            # desfaz a mais recente (aceitar)
        self.assertEqual(f.estado(), e1)
        self.assertTrue(f.desfazer()[0])            # depois a anterior (guardar)
        self.assertEqual(f.estado(), e0)
        self.assertFalse(f.desfazer()[0])           # nada mais a desfazer

    def test_desfazer_restaura_arquivo(self):
        f = Fase2()
        for a in self.SOLUCAO[:3]:
            f.executar(a)
        self.assertEqual(f.arquivo, ["E3"])
        f.desfazer()
        self.assertEqual(f.arquivo, [])

    def test_reiniciar(self):
        f = Fase2()
        for a in self.SOLUCAO:
            f.executar(a)
        f.reiniciar()
        self.assertEqual(f.estado(), (("E1", "E2", "E3", "E4", "E5", "E6"), (), ()))
        self.assertFalse(f.desfazer()[0])

    def test_sucessores_usam_as_mesmas_regras(self):
        f = Fase2()
        acoes = [a for a, _ in f.sucessores()]
        self.assertEqual(acoes, ["guardar"])        # no início, só "guardar E1" é válido
        self.assertEqual(f.estado()[0][0], "E1")    # gerar sucessores não altera o jogo


if __name__ == "__main__":
    unittest.main()
