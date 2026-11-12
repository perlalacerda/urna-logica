"""
Urna Lógica — O Enigma da Eleição de Verídia.
Ponto de entrada do jogo:   py jogo.py        (Windows)
                            python3 jogo.py   (Linux/Mac)
"""

from interface.terminal import JogoTerminal

if __name__ == "__main__":
    JogoTerminal(seed=2042).executar()
