"""
Gera as telas do jogo em docs/prints/ (para o relatório e para quem avalia).
Precisa do Playwright com Chromium:   py ferramentas/gerar_prints.py
"""

import os
from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "file://" + os.path.join(RAIZ, "jogo.html").replace(os.sep, "/")
DESTINO = os.path.join(RAIZ, "docs", "prints")

# (arquivo, tela, ações antes da foto)
TELAS = [
    ("01-inicio", "capa", []),
    ("02-menu", "menu", []),
    ("03-fase1-ordenacao", "f1", ["#f1-pecas [data-c=zona]", "#f1-pecas [data-c=secao]", "#f1-pecas [data-c=horario]", "#f1-alg [data-metodo=merge]"]),
    ("04-fase2-fila-pilha-lista", "f2", ["[data-a=guardar]", "[data-a=aceitar]"]),
    ("05-fase3-mapa", "f3", ["#f3-dica"]),
    ("06-fase4-avl", "f4", ["[data-v=nenhuma]", "#f4-prox", "[data-v=nenhuma]", "#f4-prox", "[data-v=RD]"]),
    ("07-fase5-auditoria", "f5", []),
    ("08-resolver", "solver", []),
    ("09-desafio-extra-dijkstra", "custos", []),
    ("10-dicionario", "menu", ["text=📖 Dicionário"]),
]


def main():
    os.makedirs(DESTINO, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, tela, acoes in TELAS:
            pg = b.new_page(viewport={"width": 1366, "height": 860}, device_scale_factor=1)
            pg.goto(URL)
            pg.evaluate(f"P.perfil = 'tudo'; P.capa = {'false' if tela == 'capa' else 'true'}; P.tut = {{f1:1,f2:1,f3:1,f4:1,f5:1,custos:1}}; ir('{tela}')")
            for a in acoes:
                pg.click(a)
                pg.wait_for_timeout(250)
            pg.wait_for_timeout(500)
            pg.screenshot(path=os.path.join(DESTINO, nome + ".png"))
            pg.close()
            print("ok", nome)
        b.close()


if __name__ == "__main__":
    main()
