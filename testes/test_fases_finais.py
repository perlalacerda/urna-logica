"""
Testes das Fases 4 e 5 e do gerador de cenários.

    python -m unittest -v testes.test_fases_finais
"""

import unittest

from jogo.fase4 import Fase4, PARES_ESTADOS, resposta_correta
from jogo.fase5 import Fase5
from jogo.cenarios import gerar_mapa, cenarios_de_comparacao
from jogo.fase3 import chave_estado
from algoritmos.solver import bfs, dfs_recursiva

PREVISOES_CERTAS = ["nenhuma", "nenhuma", "RD", "nenhuma", "RE", "nenhuma", "RED", "nenhuma", "RDE"]
ROTA = ["A", "C", "E", "C", "B", "H", "D", "F"]
TRIAGEM = ["guardar", "aceitar", "arquivar", "aceitar", "liberar", "arquivar", "aceitar"]


class TestFase4(unittest.TestCase):
    def test_sala1_quatro_rotacoes_da_aula(self):
        f = Fase4()
        for p in PREVISOES_CERTAS:
            r = f.inserir_proximo(p)
            self.assertTrue(r["acertou"], f"lacre {r['codigo']}")
            self.assertTrue(r["eh_avl"])
        self.assertTrue(f.sala1_completa())
        self.assertEqual(f.acertos_sala1(), 9)
        self.assertEqual(f.avl.rotacoes, {"RD": 1, "RE": 1, "RED": 1, "RDE": 1})

    def test_previsao_errada_registra_mas_insere(self):
        f = Fase4()
        f.inserir_proximo("nenhuma"); f.inserir_proximo("nenhuma")
        r = f.inserir_proximo("RE")              # o correto é RD
        self.assertFalse(r["acertou"])
        self.assertEqual(r["ocorrido"], "RD")
        self.assertEqual(r["no"], 70)
        self.assertEqual(len(f.avl), 3)

    def test_entrada_invalida_e_sala_completa(self):
        f = Fase4()
        self.assertFalse(f.inserir_proximo("girar")["ok"])
        self.assertEqual(f.proximo, 0)           # nada mudou
        for p in PREVISOES_CERTAS:
            f.inserir_proximo(p)
        self.assertFalse(f.inserir_proximo("nenhuma")["ok"])

    def test_sala2_respostas_calculadas(self):
        """Enigma 8.2: mesma posição com/sem pista -> chaves diferentes."""
        self.assertEqual(resposta_correta(*PARES_ESTADOS[0]), (False, True))
        self.assertEqual(resposta_correta(*PARES_ESTADOS[1]), (True, False))   # repetido
        self.assertEqual(resposta_correta(*PARES_ESTADOS[2]), (True, True))    # mais energia
        a, b = PARES_ESTADOS[0]
        self.assertEqual(a[0], b[0])                                           # mesma posição
        self.assertNotEqual(chave_estado(a), chave_estado(b))

    def test_selo4_exige_as_duas_salas(self):
        f = Fase4()
        for p in PREVISOES_CERTAS:
            f.inserir_proximo(p)
        self.assertFalse(f.venceu())
        for i, par in enumerate(PARES_ESTADOS):
            ok, _, _ = f.responder_par(i, *resposta_correta(*par))
            self.assertTrue(ok)
        self.assertTrue(f.venceu())

    def test_sala2_resposta_errada_nao_conclui(self):
        f = Fase4()
        f.responder_par(1, True, True)           # errado: deveria NÃO explorar
        self.assertFalse(f.sala2_completa())

    def test_sala3_busca(self):
        f = Fase4()
        for p in PREVISOES_CERTAS:
            f.inserir_proximo(p)
        achou, caminho, comps = f.consultar(42)
        self.assertTrue(achou)
        self.assertEqual(caminho, [50, 25, 42])
        achou, caminho, comps = f.consultar(43)
        self.assertFalse(achou)
        self.assertLessEqual(comps, f.avl.altura() + 1)


class TestFase5(unittest.TestCase):
    def test_trilha_consistente_com_jogador(self):
        f = Fase5()
        f.etapa_lote(algoritmo="quick")
        f.etapa_triagem(TRIAGEM)
        f.etapa_mapa(ROTA)
        self.assertTrue(f.consistente())
        self.assertIn("jogador", f.etapas["mapa"]["origem"])

    def test_integracao_com_o_historico_real_das_fases_2_e_3(self):
        """Usa os objetos das Fases 2 e 3 jogadas, como faz a interface."""
        from jogo.fase2 import Fase2
        from jogo.fase3 import Fase3
        f2, f3 = Fase2(), Fase3()
        for a in TRIAGEM:
            f2.executar(a)
        for v in ROTA[1:]:
            f3.ir_para(v)
        f = Fase5()
        f.etapa_lote()
        self.assertTrue(f.etapa_triagem(f2.acoes_feitas)["ok"])
        self.assertTrue(f.etapa_mapa(f3.trilha)["ok"])
        self.assertTrue(f.consistente())

    def test_trilha_consistente_com_solver(self):
        f = Fase5()
        for alg in ("bubble", "merge", "quick"):
            self.assertTrue(f.etapa_lote(algoritmo=alg)["ok"])
        self.assertTrue(f.etapa_triagem()["ok"])
        self.assertTrue(f.etapa_mapa()["ok"])
        self.assertIn("solver", f.etapas["triagem"]["origem"])

    def test_trilha_invalida_e_recusada(self):
        f = Fase5()
        self.assertFalse(f.etapa_mapa(["A", "C", "G", "F"])["ok"])     # sem AUT
        self.assertFalse(f.etapa_triagem(["aceitar"])["ok"])           # jogada inválida
        self.assertFalse(f.consistente())

    def test_relatorio_ordenado_com_merge(self):
        f = Fase5()
        linhas = f.comparar_estrategias()
        self.assertEqual(len(linhas), 6)                              # 2 cenários x 3 estratégias
        chaves = [(x["cenario"], x["expandidos"], x["estrategia"]) for x in linhas]
        self.assertEqual(chaves, sorted(chaves))
        texto = f.relatorio_texto()
        self.assertIn("Comparação BFS x DFS", texto)


class TestCenarios(unittest.TestCase):
    def test_gerador_reproduzivel_e_com_solucao(self):
        p1, s1 = gerar_mapa(99, n=20)
        p2, s2 = gerar_mapa(99, n=20)
        self.assertEqual(s1, s2)
        self.assertEqual([p1.G.vizinhos(v) for v in p1.G.vertices()],
                         [p2.G.vizinhos(v) for v in p2.G.vertices()])
        self.assertTrue(bfs(p1).encontrou)                            # verificador

    def test_mapa_gerado_e_conexo(self):
        from algoritmos.busca_grafo import bfs as bfs_grafo, INFINITO
        p, _ = gerar_mapa(5, n=25)
        d, *_ = bfs_grafo(p.G, p.inicio)
        self.assertNotIn(INFINITO, d.values())

    def test_dois_cenarios_bfs_nunca_pior(self):
        for nome, p in cenarios_de_comparacao():
            with self.subTest(cenario=nome):
                self.assertLessEqual(bfs(p).numero_acoes(), dfs_recursiva(p).numero_acoes())


if __name__ == "__main__":
    unittest.main()
