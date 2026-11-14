"""
Registros de votação fictícios da cidade de Verídia (Fase 1).

Campos (tabela da seção 5.1 do enunciado):
    id_registro  "VR-0081"   identificador único; não pode se repetir
    zona         "03"        código da zona
    secao        "014"       código da seção
    opcao        "24"        código de opção (fictício)
    timestamp    "18:42:10"  horário de processamento no cenário
    status       "PENDENTE"  PENDENTE, CONFERIDO ou DIVERGENTE

Por que zona, seção e horário são TEXTOS com zeros à esquerda?
    Como têm tamanho fixo ("03", "014", "18:42:10"), a ordem alfabética
    coincide com a ordem numérica/cronológica. Assim a comparação é direta.

Aleatoriedade reproduzível:
    Tudo que é sorteado usa random.Random(seed). A mesma seed gera sempre
    os mesmos registros na mesma ordem — requisito RF03 e seção 3 do EP.
"""

import random

STATUS_VALIDOS = ("PENDENTE", "CONFERIDO", "DIVERGENTE")


class Registro:
    def __init__(self, id_registro, zona, secao, opcao, timestamp, status="PENDENTE"):
        if status not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {status}")
        self.id_registro = id_registro
        self.zona = zona
        self.secao = secao
        self.opcao = opcao
        self.timestamp = timestamp
        self.status = status

    def linha(self):
        return (f"{self.id_registro}  zona {self.zona}  seção {self.secao}  "
                f"opção {self.opcao}  {self.timestamp}  {self.status}")

    def __repr__(self):
        return f"Registro({self.id_registro})"


# ------------------------------------------------------------ critérios
# Cada critério é uma função que transforma o registro em algo comparável.
CRITERIOS = {
    "id": lambda r: r.id_registro,
    "zona": lambda r: (r.zona, r.id_registro),
    "horario": lambda r: (r.timestamp, r.id_registro),
    # chave composta do enigma 5.3: zona -> seção -> horário (-> id, desempate)
    "auditoria": lambda r: (r.zona, r.secao, r.timestamp, r.id_registro),
}

DESCRICAO_CRITERIOS = {
    "id": "identificador",
    "zona": "zona (desempate por identificador)",
    "horario": "horário (desempate por identificador)",
    "auditoria": "zona, depois seção, depois horário (desempate por identificador)",
}

# ------------------------------------------------------------ chave montada pelo jogador
# No jogo do navegador, a jogadora MONTA a chave composta escolhendo a ordem
# destas peças. É o conceito de chave composta (tupla comparada campo a campo),
# jogado: (zona, seção, horário) compara primeiro a zona; só se empatar,
# a seção; só se empatar de novo, o horário.
CAMPOS = {
    "zona": lambda r: r.zona,
    "secao": lambda r: r.secao,
    "horario": lambda r: r.timestamp,
    "id": lambda r: r.id_registro,
}
NOMES_CAMPOS = {"zona": "zona", "secao": "seção", "horario": "horário", "id": "identificador"}


def chave_composta(campos):
    """
    Chave = tupla com os campos na ordem escolhida. O identificador entra no fim
    como desempate (se ainda não estiver), como nos critérios fixos.
    """
    campos = list(campos)
    if not campos or any(c not in CAMPOS for c in campos) or len(set(campos)) != len(campos):
        raise ValueError(f"Chave inválida: {campos}")
    usados = campos + ([] if "id" in campos else ["id"])
    return lambda r: tuple(CAMPOS[c](r) for c in usados)


def descrever_chave(campos):
    return ", depois ".join(NOMES_CAMPOS[c] for c in campos) + ("" if "id" in campos else " (desempate por identificador)")


# ------------------------------------------------------------ geração
def gerar_registros(n, seed, zonas=3, secoes_por_zona=4):
    """
    Gera n registros fictícios, já em ordem de id. Reproduzível pela seed.
    Para criar o "enigma" do enunciado, alguns horários se repetem de
    propósito em zonas diferentes.
    """
    rng = random.Random(seed)
    horarios_base = [f"18:{m:02d}:{s:02d}" for m in range(0, 60, 7) for s in (0, 10, 30)]
    # sorteia poucos horários (cerca de n/3) para que alguns SE REPITAM
    horarios_base = rng.sample(horarios_base, max(2, min(len(horarios_base), n // 3)))
    registros = []
    for k in range(1, n + 1):
        zona = f"{rng.randint(1, zonas):02d}"
        secao = f"{rng.randint(1, secoes_por_zona):03d}"
        opcao = f"{rng.choice([10, 15, 24, 33, 40]):02d}"
        horario = rng.choice(horarios_base)        # repetições são esperadas
        status = rng.choice(STATUS_VALIDOS)
        registros.append(Registro(f"VR-{k:04d}", zona, secao, opcao, horario, status))
    return registros


def embaralhar(A, seed):
    """
    Embaralhamento de Fisher-Yates, implementado pela equipe.
    Para i de n-1 até 1: sorteia j em [0, i] e troca A[i] com A[j].
    Cada uma das n! permutações tem a mesma chance.  O(n)
    """
    rng = random.Random(seed)
    for i in range(len(A) - 1, 0, -1):
        j = rng.randint(0, i)
        A[i], A[j] = A[j], A[i]
    return A


def validar_ids_unicos(registros):
    """Devolve a lista de ids repetidos (vazia se está tudo certo). O(n)"""
    vistos, repetidos = set(), []
    for r in registros:
        if r.id_registro in vistos:
            repetidos.append(r.id_registro)
        vistos.add(r.id_registro)
    return repetidos
