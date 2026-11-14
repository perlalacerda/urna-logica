"""
O jogo no navegador NÃO tem regras próprias: só consulta tabelas que o
Python calculou com as regras do jogo. Estes testes conferem que as tabelas
concordam com o código Python em cada fase.
    python -m unittest -v testes.test_jogo_web
"""

import json
import os
import re
import tempfile
import unittest

from interface.jogo_web import gerar_dados, gerar_html
from jogo.fase1 import Fase1
from jogo.fase2 import Fase2
from jogo.fase3 import construir_mapa, mover, estado_inicial
from jogo.fase4 import Fase4


class TestJogoWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = gerar_dados()

    def test_pagina_autocontida(self):
        with tempfile.TemporaryDirectory() as d:
            with open(gerar_html(os.path.join(d, "j.html")), encoding="utf-8") as arq:
                html = arq.read()
        self.assertNotIn("/*__DADOS__*/", html)
        self.assertEqual(re.findall(r'(?:src|href)="https?://', html), [])

    def test_fase1_igual_ao_python(self):
        for chave, r in self.D["fase1"]["resultados"].items():
            alg, crit = chave.split("|")
            f = Fase1()
            esperado = f.ordenar(alg, crit)
            self.assertEqual(r["aceito"], esperado["aceito"], chave)
            self.assertEqual([x[0] for x in r["registros"]], [x.id_registro for x in f.registros])
        self.assertTrue(self.D["fase1"]["resultados"]["merge|auditoria"]["aceito"])
        self.assertFalse(self.D["fase1"]["resultados"]["merge|horario"]["aceito"])

    def test_fase2_cada_jogada_igual_ao_python(self):
        E = self.D["fase2"]["estados"]
        for e in E:
            estado = (tuple(e["fila"]), tuple(e["pilha"]), tuple(e["custodia"]))
            for acao, r in e["acoes"].items():
                f = Fase2.a_partir_do_estado(estado)
                ok, msg = f.executar(acao)
                self.assertEqual((ok, msg), (r["ok"], r["msg"]))
                if ok:
                    d = E[r["destino"]]
                    self.assertEqual(f.estado(), (tuple(d["fila"]), tuple(d["pilha"]), tuple(d["custodia"])))
        self.assertEqual(sum(e["venceu"] for e in E), 1)

    def test_fase3_cada_movimento_igual_ao_python(self):
        G, E = construir_mapa(), self.D["fase3"]["estados"]
        for e in E:
            estado = (e["pos"], tuple(e["pistas"]), tuple(e["portas"]), e["energia"])
            for v, r in e["movs"].items():
                ok, novo, msg = mover(G, estado, v)
                self.assertEqual((ok, msg), (r["ok"], r["msg"]))
                if ok:
                    d = E[r["destino"]]
                    self.assertEqual(novo, (d["pos"], tuple(d["pistas"]), tuple(d["portas"]), d["energia"]))
        self.assertEqual((E[0]["pos"], E[0]["energia"]), (estado_inicial()[0], estado_inicial()[3]))

    def test_seguir_as_dicas_da_pagina_vence(self):
        E = self.D["fase3"]["estados"]
        i, trilha = 0, ["A"]
        while not E[i]["venceu"]:
            v = re.search(r"ir para ([A-I]) ", E[i]["dica"]).group(1)
            i = E[i]["movs"][v]["destino"]
            trilha.append(v)
        self.assertEqual(trilha, ["A", "C", "E", "C", "B", "H", "D", "F"])

    def test_fase4_rotacoes_iguais_ao_python(self):
        f = Fase4()
        for q in self.D["fase4"]["lacres"]:
            self.assertEqual(q["rotacao"], f.inserir_proximo("nenhuma")["ocorrido"])
        self.assertEqual(self.D["fase4"]["consultas"]["42"]["caminho"] if "42" in self.D["fase4"]["consultas"]
                         else self.D["fase4"]["consultas"][42]["caminho"], [50, 25, 42])

    def test_dados_serializaveis(self):
        json.dumps(self.D, ensure_ascii=False, default=str)


if __name__ == "__main__":
    unittest.main()
