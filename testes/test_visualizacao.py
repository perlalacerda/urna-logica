"""
Teste da visualização: a página é gerada a partir da execução real e não
depende de internet.     python -m unittest -v testes.test_visualizacao
"""

import json
import os
import re
import tempfile
import unittest

from interface.visualizacao import gerar_html, dados_avl, dados_busca, VetorRastreado
from algoritmos.ordenacao import bubble_sort


class TestVisualizacao(unittest.TestCase):
    def test_pagina_autocontida(self):
        with tempfile.TemporaryDirectory() as d:
            caminho = gerar_html(os.path.join(d, "v.html"))
            html = open(caminho, encoding="utf-8").read()
        self.assertNotIn("/*__DADOS__*/", html)                         # dados foram embutidos
        self.assertEqual(re.findall(r'(?:src|href)="https?://', html), [])   # nada externo
        bloco = html.split("const DADOS = ", 1)[1].split(";\n", 1)[0]
        dados = json.loads(bloco)
        self.assertEqual(set(dados), {"busca", "avl", "triagem", "ordenacao", "metricas"})

    def test_dados_vem_da_execucao_real(self):
        avl = dados_avl()
        self.assertEqual([q["rotacao"] for q in avl["quadros"]],
                         ["nenhuma", "nenhuma", "RD", "nenhuma", "RE", "nenhuma", "RED", "nenhuma", "RDE"])
        bfs = dados_busca()["estrategias"]["BFS"]
        self.assertEqual(bfs["caminho"], ["A", "C", "E", "C", "B", "H", "D", "F"])
        self.assertEqual(len(bfs["quadros"]), bfs["resumo"]["expandidos"])

    def test_vetor_rastreado_registra_escritas(self):
        A = VetorRastreado([3, 1, 2])
        bubble_sort(A)
        self.assertEqual(A, [1, 2, 3])
        self.assertEqual(A.fotos[-1]["v"], [1, 2, 3])
        self.assertGreater(len(A.fotos), 1)


if __name__ == "__main__":
    unittest.main()
