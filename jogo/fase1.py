"""
FASE 1 — O Arquivo Embaralhado                       (seção 5 do enunciado)

Conceitos: vetor de registros, aleatoriedade com seed, Bubble/Merge/Quick
Sort, chave composta, contagem de comparações e movimentações.

Regra da auditoria (enigma 5.3), escrita como condição verificável:
    O lote é ACEITO  <=>  para todo i, chave(A[i]) <= chave(A[i+1]),
    onde chave(r) = (zona, seção, horário, id_registro).

    O id_registro entra como último critério de desempate: torna a ordem
    final única, qualquer que seja o algoritmo (ver docs/decisoes.md).

Como se ganha o selo: ordenar o lote de modo que a regra acima valha.
O jogador escolhe o algoritmo e o critério; se escolher um critério que não
é o da auditoria (ex.: só horário), o jogo mostra o PRIMEIRO ponto em que
a ordem da auditoria foi violada.
"""

from algoritmos.ordenacao import ordenar, primeiro_fora_de_ordem, ALGORITMOS
from jogo.registros import (CRITERIOS, DESCRICAO_CRITERIOS, gerar_registros,
                            embaralhar, validar_ids_unicos)

CHAVE_AUDITORIA = CRITERIOS["auditoria"]


class Fase1:
    NOME = "Fase 1 — O Arquivo Embaralhado"
    ABERTURA = ("Alerta: o arquivo de registros chegou fora de ordem.\n"
                "A sequência original foi perdida.\n"
                "Antes de investigar, precisamos organizar os dados sem perder nenhum registro.")
    ENIGMA = ("A auditoria só aceita o lote ordenado por ZONA, depois por SEÇÃO e,\n"
              "em caso de empate, por HORÁRIO. Atenção: há registros com o mesmo\n"
              "horário em zonas diferentes. Qual critério garante a ordem pedida?")

    def __init__(self, seed=2042, n=12):
        self.seed = seed
        self.n = n
        self.reiniciar()

    def reiniciar(self):
        """Recarrega o mesmo lote embaralhado (mesma seed = mesmo lote)."""
        self.registros = embaralhar(gerar_registros(self.n, self.seed), self.seed + 1)
        repetidos = validar_ids_unicos(self.registros)
        if repetidos:
            raise ValueError(f"Lote inválido: ids repetidos {repetidos}")
        self.selo = False
        self.tentativas = []            # histórico: (algoritmo, critério, contador, aceito)

    def ordenar(self, algoritmo, criterio):
        """
        Executa a ordenação escolhida pelo jogador.
        Devolve um dicionário com o resultado, pronto para exibir.
        """
        if algoritmo not in ALGORITMOS:
            return {"ok": False, "mensagem": f"Algoritmo desconhecido: {algoritmo}."}
        if criterio not in CRITERIOS:
            return {"ok": False, "mensagem": f"Critério desconhecido: {criterio}."}

        quantidade_antes = len(self.registros)
        contador = ordenar(self.registros, algoritmo, CRITERIOS[criterio])
        assert len(self.registros) == quantidade_antes      # nenhum registro perdido

        erro = primeiro_fora_de_ordem(self.registros, CHAVE_AUDITORIA)
        aceito = erro == -1
        if aceito:
            self.selo = True
            mensagem = "Lote ACEITO pela auditoria. Selo 1 conquistado!"
        else:
            a, b = self.registros[erro], self.registros[erro + 1]
            mensagem = (f"Lote RECUSADO. Primeiro ponto fora da ordem da auditoria: "
                        f"posições {erro} e {erro + 1}.\n"
                        f"  {a.linha()}\n  {b.linha()}\n"
                        f"Dica: você ordenou por '{DESCRICAO_CRITERIOS[criterio]}'. "
                        f"A auditoria exige zona, depois seção, depois horário.")
        self.tentativas.append((algoritmo, criterio, contador, aceito))
        return {"ok": True, "aceito": aceito, "contador": contador,
                "posicao_erro": erro, "mensagem": mensagem}

    def comparar_algoritmos(self, tamanhos=(10, 100, 500), seed=None):
        """
        Roda os três algoritmos sobre CÓPIAS do mesmo lote, para cada tamanho.
        Devolve linhas (tamanho, algoritmo, comparações, movimentações, ms).
        Não altera o lote do jogador.
        """
        seed = self.seed if seed is None else seed
        linhas = []
        for n in tamanhos:
            base = embaralhar(gerar_registros(n, seed), seed + 1)
            for nome in ALGORITMOS:
                copia = list(base)
                c = ordenar(copia, nome, CHAVE_AUDITORIA)
                linhas.append((n, c.algoritmo, c.comparacoes, c.movimentacoes, c.tempo_ms))
        return linhas
