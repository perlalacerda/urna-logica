"""
Testes de ordenação e registros (seção 15 do enunciado).

    python -m unittest -v testes.test_ordenacao

Casos da seção 15: já ordenado, ordem inversa, repetidos, chave composta,
vetor vazio, um elemento; comparar o resultado dos três algoritmos.
Registros: vetor vazio, um registro, ids repetidos, carga válida, seed reproduzível.
"""

import unittest
from collections import Counter

from algoritmos.ordenacao import (bubble_sort, bubble_sort_recursivo, merge_sort,
                                  quick_sort, quick_sort_versao_do_slide,
                                  primeiro_fora_de_ordem, ordenar)
from jogo.registros import (Registro, CRITERIOS, gerar_registros, embaralhar,
                            validar_ids_unicos)

TODOS = [bubble_sort, bubble_sort_recursivo, merge_sort, quick_sort]

CASOS = {
    "vazio": [],
    "um elemento": [7],
    "já ordenado": [1, 2, 3, 4, 5, 6],
    "ordem inversa": [6, 5, 4, 3, 2, 1],
    "repetidos": [3, 1, 3, 2, 1, 3],
    "exemplo bubble (aula 02)": [-2, 45, 0, 11, -9],
    "exemplo merge (aula 02)": [12, 35, 87, 26, 9, 28, 7],
    "exemplo quick (aula 04)": [2, 8, 7, 1, 3, 5, 6, 4],
}


class TestAlgoritmos(unittest.TestCase):
    def test_todos_os_casos(self):
        for nome, dados in CASOS.items():
            for alg in TODOS:
                with self.subTest(caso=nome, algoritmo=alg.__name__):
                    A = list(dados)
                    alg(A)
                    self.assertEqual(A, sorted(dados))              # ordem correta
                    self.assertEqual(Counter(A), Counter(dados))    # nada perdido/duplicado

    def test_contadores_bubble(self):
        A = [5, 4, 3, 2, 1]
        c = bubble_sort(A)
        self.assertEqual(c.comparacoes, 10)       # n(n-1)/2 = 5*4/2
        self.assertEqual(c.movimentacoes, 30)     # 10 trocas x 3

    def test_quick_versao_literal_do_slide_nao_termina(self):
        """
        Demonstra a armadilha: com recursão em p..q, o pivô máximo
        faz q = r e a mesma chamada se repete indefinidamente.
        """
        with self.assertRaises(RecursionError):
            quick_sort_versao_do_slide([3, 1, 2])

    def test_primeiro_fora_de_ordem(self):
        self.assertEqual(primeiro_fora_de_ordem([1, 2, 5, 4, 6]), 2)
        self.assertEqual(primeiro_fora_de_ordem([1, 2, 3]), -1)
        self.assertEqual(primeiro_fora_de_ordem([]), -1)

    def test_algoritmo_invalido(self):
        with self.assertRaises(ValueError):
            ordenar([1], "heap")


class TestChaveComposta(unittest.TestCase):
    def setUp(self):
        # mesmo horário em zonas diferentes, como pede o enigma 5.3
        self.dados = [
            Registro("VR-0005", "02", "001", "10", "18:00:00"),
            Registro("VR-0001", "01", "002", "15", "18:00:00"),
            Registro("VR-0003", "01", "001", "24", "18:30:00"),
            Registro("VR-0002", "01", "001", "24", "18:10:00"),
            Registro("VR-0004", "02", "001", "33", "17:59:59"),
        ]
        self.esperado = ["VR-0002", "VR-0003", "VR-0001", "VR-0004", "VR-0005"]

    def test_tres_algoritmos_concordam(self):
        for alg in TODOS:
            with self.subTest(algoritmo=alg.__name__):
                A = list(self.dados)
                alg(A, CRITERIOS["auditoria"])
                self.assertEqual([r.id_registro for r in A], self.esperado)

    def test_so_pelo_horario_nao_basta(self):
        """Ordenar só pelo horário viola a regra da auditoria (zona primeiro)."""
        A = list(self.dados)
        merge_sort(A, CRITERIOS["horario"])
        self.assertNotEqual(primeiro_fora_de_ordem(A, CRITERIOS["auditoria"]), -1)


class TestRegistros(unittest.TestCase):
    def test_seed_reproduzivel(self):
        a = [r.linha() for r in embaralhar(gerar_registros(30, seed=42), seed=7)]
        b = [r.linha() for r in embaralhar(gerar_registros(30, seed=42), seed=7)]
        c = [r.linha() for r in embaralhar(gerar_registros(30, seed=42), seed=8)]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_embaralhar_nao_perde_registros(self):
        regs = gerar_registros(50, seed=1)
        ids = sorted(r.id_registro for r in regs)
        embaralhar(regs, seed=3)
        self.assertEqual(sorted(r.id_registro for r in regs), ids)

    def test_vazio_e_um_registro(self):
        self.assertEqual(gerar_registros(0, seed=1), [])
        self.assertEqual(embaralhar([], seed=1), [])
        um = gerar_registros(1, seed=1)
        self.assertEqual(len(embaralhar(um, seed=1)), 1)

    def test_ids_repetidos_sao_detectados(self):
        regs = gerar_registros(3, seed=1)
        regs.append(Registro(regs[0].id_registro, "01", "001", "10", "18:00:00"))
        self.assertEqual(validar_ids_unicos(regs), [regs[0].id_registro])
        self.assertEqual(validar_ids_unicos(gerar_registros(100, seed=2)), [])

    def test_status_invalido(self):
        with self.assertRaises(ValueError):
            Registro("VR-1", "01", "001", "10", "18:00:00", status="XYZ")

    def test_carga_grande_tres_algoritmos(self):
        base = embaralhar(gerar_registros(300, seed=11), seed=12)
        resultados = []
        for alg in TODOS:
            A = list(base)
            alg(A, CRITERIOS["auditoria"])
            self.assertEqual(primeiro_fora_de_ordem(A, CRITERIOS["auditoria"]), -1)
            resultados.append([r.id_registro for r in A])
        self.assertTrue(all(r == resultados[0] for r in resultados))


if __name__ == "__main__":
    unittest.main()
