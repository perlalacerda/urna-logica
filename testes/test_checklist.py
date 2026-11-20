"""
A matriz de inspeção (docs/checklist-entrega.md) só cita funções e testes que existem.

    python -m unittest -v testes.test_checklist
"""

import unittest

from ferramentas import gerar_checklist as g


class TestChecklist(unittest.TestCase):
    def test_cada_funcao_citada_existe(self):
        for linha in g.LINHAS:
            for ref in linha[2]:
                arquivo, n = g.onde(ref)
                self.assertTrue(arquivo.endswith(".py") and n > 0, ref)

    def test_cada_teste_citado_existe(self):
        for linha in g.LINHAS:
            for ref in linha[4]:
                arquivo, n = g.onde_teste(ref)
                self.assertTrue(arquivo.startswith("testes/") and n > 0, ref)

    def test_cobre_os_conteudos_da_secao_10(self):
        texto = " ".join(l[0] for l in g.LINHAS).lower()
        for tema in ("vetor", "bubble", "merge", "quick", "pilha", "fila", "lista ligada", "grafo",
                     "bfs", "dfs", "árvore de busca", "avl", "recursivo", "estado"):
            self.assertIn(tema, texto)


if __name__ == "__main__":
    unittest.main()
