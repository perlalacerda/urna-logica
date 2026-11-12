"""
Narrativa do jogo — fonte ÚNICA dos textos da história.
Usada pela interface em terminal e pela visualização em HTML, para que a
história seja a mesma nos dois lugares.

Baseada na seção 2 do enunciado do EP. Cidade, pessoas, registros e códigos
são inteiramente fictícios; o jogo é apartidário e não usa nomes, partidos,
números ou resultados de eleições reais.
"""

from jogo.fase1 import Fase1
from jogo.fase2 import Fase2
from jogo.fase3 import Fase3
from jogo.fase4 import Fase4
from jogo.fase5 import Fase5

TITULO = "Urna Lógica — O Enigma da Eleição de Verídia"

PROLOGO = [
    "É o ano de 2042. A cidade de Verídia acaba de realizar sua eleição municipal.",
    "Ao final da apuração, uma falha de sincronização atingiu o sistema de auditoria. "
    "Nenhum registro foi necessariamente alterado — mas os dados ficaram fora de ordem, "
    "conexões entre os locais de votação foram interrompidas e parte da trilha de "
    "processamento não pode mais ser consultada diretamente.",
    "A Comissão Independente de Verificação (CIV), uma entidade apartidária, convoca você: "
    "Analista de Integridade de Dados.",
    "A pergunta da CIV é simples: é possível reconstruir uma trilha coerente entre os "
    "registros de origem, os locais de votação e o relatório final, respeitando todas as regras?",
    "Sua missão é recuperar os cinco selos de auditoria e chegar ao Cofre de Verificação. "
    "O objetivo não é favorecer candidato algum: é verificar, com regras explícitas e "
    "dados claros, se a apuração simulada pode ser reconstruída.",
]

AVISO = ("Verídia, seus locais, registros, códigos e candidatos são inteiramente fictícios. "
         "Finalidade acadêmica: exercitar lógica, estruturas de dados e algoritmos.")

# Cada capítulo: o selo, a fase, a mensagem de abertura (do enunciado) e o que está em jogo.
CAPITULOS = [
    {"selo": 1, "fase": Fase1.NOME, "abertura": Fase1.ABERTURA,
     "missao": "Organizar o lote de registros na ordem exigida pela auditoria, sem perder nenhum.",
     "ferramentas": "vetor de registros, seed, Bubble, Merge e Quick Sort, chave composta"},
    {"selo": 2, "fase": Fase2.NOME, "abertura": Fase2.ABERTURA,
     "missao": "Montar a sequência de custódia E2 → E4 → E1 → E6 a partir da fila de chegada.",
     "ferramentas": "fila (FIFO), pilha (LIFO) e desfazer, lista ligada"},
    {"selo": 3, "fase": Fase3.NOME, "abertura": Fase3.ABERTURA,
     "missao": "Ir da Central de Auditoria ao Centro de Validação passando pela autenticação.",
     "ferramentas": "grafo, lista de adjacência, estado, BFS e DFS, árvore de busca"},
    {"selo": 4, "fase": Fase4.NOME, "abertura": Fase4.ABERTURA,
     "missao": "Organizar a memória do sistema para não investigar o mesmo estado duas vezes.",
     "ferramentas": "árvore AVL, rotações, chave de estado"},
    {"selo": 5, "fase": Fase5.NOME, "abertura": Fase5.ABERTURA,
     "missao": "Reconstruir a trilha completa e provar que ela decorre das regras.",
     "ferramentas": "integração, solver, métricas, ordenação do relatório"},
]

EPILOGO = [
    "Os cinco selos foram reunidos e o Cofre de Verificação se abriu.",
    "A trilha de auditoria de Verídia foi reconstruída a partir de regras explícitas: "
    "o lote foi ordenado sem perdas, as evidências seguiram a cadeia de custódia, a rota "
    "passou pela autenticação antes da validação e nenhum estado foi investigado à toa.",
    "A CIV registra em ata: a apuração simulada é consistente com as regras do cenário.",
]
