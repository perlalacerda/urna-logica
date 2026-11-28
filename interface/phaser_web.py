"""
Gera phaser/dados.js: os dados da Fase 3 calculados pelo Python, para a versão em Phaser.

A versão Phaser só DESENHA e ANIMA. As regras (adjacência, portas, pistas, energia),
as 160 situações possíveis e a dica de cada uma vêm de jogo/fase3.py e do solver,
exatamente como no jogo do navegador (interface/jogo_web.py). Assim as duas versões
nunca divergem: mudar uma regra no Python muda as duas.

Uso:  python -m interface.phaser_web
"""
import base64
import json
import os

from algoritmos.solver import bfs, dfs_recursiva
from interface.jogo_web import dados_fase3
from jogo.fase3 import ProblemaMapa

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dados_phaser():
    d = dados_fase3()
    b, f = bfs(ProblemaMapa()), dfs_recursiva(ProblemaMapa())
    d["solver"] = {"bfs": {"acoes": b.numero_acoes(), "fronteira": b.maior_fronteira, "rota": [e[0] for _, e in b.caminho]},
                   "dfs": {"acoes": f.numero_acoes(), "fronteira": f.maior_fronteira, "rota": [e[0] for _, e in f.caminho]}}
    return d


def gerar(pasta=os.path.join(RAIZ, "phaser")):
    os.makedirs(pasta, exist_ok=True)
    img = open(os.path.join(RAIZ, "interface", "miss_pearl.webp"), "rb").read()
    texto = ("// Gerado por interface/phaser_web.py — não editar à mão.\n"
             "window.D3 = " + json.dumps(dados_phaser(), ensure_ascii=False) + ";\n"
             "window.MISS_PEARL = \"data:image/webp;base64," + base64.b64encode(img).decode() + "\";\n")
    with open(os.path.join(pasta, "dados.js"), "w", encoding="utf-8") as arq:
        arq.write(texto)
    return os.path.join(pasta, "dados.js")


if __name__ == "__main__":
    print(gerar())
