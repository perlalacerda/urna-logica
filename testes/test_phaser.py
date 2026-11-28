"""Versão Phaser da Fase 3: os dados vêm do Python e precisam estar em dia."""
import os
import unittest

from interface.phaser_web import RAIZ, dados_phaser


class TestPhaser(unittest.TestCase):
    def test_dados_vem_das_regras_e_do_solver(self):
        d = dados_phaser()
        self.assertEqual(len(d["estados"]), 160)                     # todas as situações alcançáveis
        self.assertEqual(d["solver"]["bfs"]["acoes"], 7)
        self.assertEqual(d["solver"]["bfs"]["rota"], list("ACECBHDF"))
        self.assertEqual(d["solver"]["dfs"]["acoes"], 10)
        self.assertEqual(d["curto"], list("ACGF"))                    # o atalho que a porta recusa
        inicial = d["estados"][0]
        self.assertEqual((inicial["pos"], inicial["energia"]), ("A", 10))

    def test_arquivo_gerado_esta_em_dia(self):
        """phaser/dados.js precisa ser o que o Python gera hoje (rode python -m interface.phaser_web)."""
        import json
        texto = open(os.path.join(RAIZ, "phaser", "dados.js"), encoding="utf-8").read()
        self.assertIn("window.D3 = " + json.dumps(dados_phaser(), ensure_ascii=False) + ";", texto)

    def test_pagina_nao_tem_regras_proprias(self):
        html = open(os.path.join(RAIZ, "phaser", "index.html"), encoding="utf-8").read()
        self.assertIn('src="dados.js"', html)
        self.assertIn('src="phaser.min.js"', html)                    # funciona sem internet
        self.assertNotIn("SEQ\" &&", html)                            # nenhuma regra de porta escrita em JS


if __name__ == "__main__":
    unittest.main()
