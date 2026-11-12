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
            with open(caminho, encoding="utf-8") as arq:
                html = arq.read()
        self.assertNotIn("/*__DADOS__*/", html)                         # dados foram embutidos
        self.assertEqual(re.findall(r'(?:src|href)="https?://', html), [])   # nada externo
        bloco = html.split("const D = ", 1)[1].split(";\n", 1)[0]
        dados = json.loads(bloco)
        self.assertTrue({"busca", "avl", "triagem", "ordenacao", "metricas", "narrativa", "auditoria",
                         "lote", "triagem_jogavel", "mapa_jogavel", "pares"} <= set(dados))
        self.assertEqual(len(dados["narrativa"]["capitulos"]), 5)       # um capítulo por selo
        self.assertTrue(dados["auditoria"]["consistente"])              # Fase 5 executada de verdade

    def test_dados_vem_da_execucao_real(self):
        avl = dados_avl()
        self.assertEqual([q["rotacao"] for q in avl["quadros"]],
                         ["nenhuma", "nenhuma", "RD", "nenhuma", "RE", "nenhuma", "RED", "nenhuma", "RDE"])
        bfs = dados_busca()["estrategias"]["BFS"]
        self.assertEqual(bfs["caminho"], ["A", "C", "E", "C", "B", "H", "D", "F"])
        self.assertEqual(len(bfs["quadros"]), bfs["resumo"]["expandidos"])

    def test_jogos_da_pagina_usam_as_regras_do_python(self):
        """A página não tem regras próprias: só consulta tabelas calculadas pelo jogo."""
        from interface.visualizacao import dados_triagem_jogavel, dados_mapa_jogavel
        from jogo.fase2 import Fase2
        t = dados_triagem_jogavel()
        self.assertEqual(len(t["estados"]), 14)
        self.assertEqual(sum(e["venceu"] for e in t["estados"]), 1)
        self.assertEqual(t["estados"][0]["acoes"]["aceitar"]["msg"], Fase2().executar("aceitar")[1])
        m = dados_mapa_jogavel()
        e, rota = 0, ["C", "E", "C", "B", "H", "D", "F"]
        for v in rota:                                # a rota válida chega ao destino pela tabela
            r = m["estados"][e]["movs"][v]
            self.assertTrue(r["ok"], r["msg"])
            e = r["destino"]
        self.assertTrue(m["estados"][e]["venceu"])
        self.assertFalse(m["estados"][0]["movs"]["C"]["ok"] is False)
        # caminho curto A-C-G-F: a porta de F recusa
        e = m["estados"][0]["movs"]["C"]["destino"]
        e = m["estados"][e]["movs"]["G"]["destino"]
        self.assertFalse(m["estados"][e]["movs"]["F"]["ok"])

    def test_animacao_de_ordenacao_sem_fichas_duplicadas(self):
        from interface.visualizacao import dados_lote
        for nome, a in dados_lote()["algoritmos"].items():
            for q in a["quadros"]:
                self.assertEqual(len(set(q["ids"])), 12, nome)

    def test_vetor_rastreado_registra_escritas(self):
        A = VetorRastreado([3, 1, 2])
        bubble_sort(A)
        self.assertEqual(A, [1, 2, 3])
        self.assertEqual(A.fotos[-1]["v"], [1, 2, 3])
        self.assertGreater(len(A.fotos), 1)


if __name__ == "__main__":
    unittest.main()
