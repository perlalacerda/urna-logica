"""
Testes das estruturas de dados (seção 15 do enunciado).

Rodar, a partir da pasta do projeto:
    python -m unittest -v testes.test_estruturas

Casos cobertos (tabela da seção 15):
    Pilha ...... vazia, um elemento, múltiplos push/pop, topo, pop vazia
    Fila ....... vazia, um elemento, múltiplos enqueue/dequeue, ordem FIFO, dequeue vazia
    Lista ...... inserção início/meio/fim, remoção início/meio/fim, busca, vazia, inexistente
    AVL ........ rotações RD, RE, RED, RDE, chave duplicada, busca existente/inexistente
"""

import unittest

from estruturas.pilha import Pilha
from estruturas.fila import Fila
from estruturas.lista_ligada import ListaLigada
from estruturas.avl import ArvoreAVL, fator_balanceamento


class TestPilha(unittest.TestCase):
    def test_pilha_vazia(self):
        p = Pilha()
        self.assertTrue(p.esta_vazia())
        self.assertEqual(p.pop(), (False, None))    # pop em pilha vazia: sem erro
        self.assertEqual(p.peek(), (False, None))

    def test_um_elemento(self):
        p = Pilha()
        p.push("E1")
        self.assertEqual(p.peek(), (True, "E1"))
        self.assertEqual(p.pop(), (True, "E1"))
        self.assertTrue(p.esta_vazia())

    def test_lifo_varios_elementos(self):
        p = Pilha()
        for e in ["A1", "A2", "A3"]:
            p.push(e)
        # o último a entrar é o primeiro a sair
        self.assertEqual([p.pop()[1] for _ in range(3)], ["A3", "A2", "A1"])
        self.assertEqual(p.maior_tamanho, 3)

    def test_pop_vazia_nao_corrompe(self):
        p = Pilha()
        p.push(1)
        p.pop()
        self.assertEqual(p.pop(), (False, None))
        p.push(2)
        self.assertEqual(p.para_lista(), [2])
        self.assertEqual(len(p), 1)


class TestFila(unittest.TestCase):
    def test_fila_vazia(self):
        f = Fila()
        self.assertTrue(f.esta_vazia())
        self.assertEqual(f.dequeue(), (False, None))
        self.assertEqual(f.peek(), (False, None))

    def test_um_elemento(self):
        f = Fila()
        f.enqueue("E1")
        self.assertEqual(f.peek(), (True, "E1"))
        self.assertEqual(f.dequeue(), (True, "E1"))
        self.assertTrue(f.esta_vazia())
        self.assertIsNone(f.final)       # linha 6 do dequeue: fila ficou vazia

    def test_ordem_fifo(self):
        f = Fila()
        for e in ["E1", "E2", "E3", "E4", "E5", "E6"]:
            f.enqueue(e)
        self.assertEqual([f.dequeue()[1] for _ in range(6)],
                         ["E1", "E2", "E3", "E4", "E5", "E6"])

    def test_intercalado(self):
        f = Fila()
        f.enqueue(1); f.enqueue(2)
        self.assertEqual(f.dequeue(), (True, 1))
        f.enqueue(3)
        self.assertEqual(f.para_lista(), [2, 3])
        self.assertEqual(f.maior_tamanho, 2)


class TestListaLigada(unittest.TestCase):
    def test_lista_vazia(self):
        l = ListaLigada()
        self.assertTrue(l.esta_vazia())
        self.assertEqual(l.primeiro(), (False, None))
        self.assertEqual(l.ultimo_elemento(), (False, None))
        self.assertIsNone(l.buscar("X"))
        self.assertFalse(l.remover("X"))
        self.assertEqual(l.remover_inicio(), (False, None))
        self.assertEqual(l.remover_fim(), (False, None))

    def test_insercao_inicio_meio_fim(self):
        l = ListaLigada()
        l.inserir_fim("E4")                 # fim (lista vazia)
        l.inserir_inicio("E2")              # início
        l.inserir_fim("E6")                 # fim
        l.inserir_apos("E4", "E1")          # meio
        self.assertEqual(l.percorrer(), ["E2", "E4", "E1", "E6"])
        self.assertEqual(l.primeiro(), (True, "E2"))
        self.assertEqual(l.ultimo_elemento(), (True, "E6"))
        self.assertEqual(len(l), 4)

    def test_inserir_apos_inexistente(self):
        l = ListaLigada()
        l.inserir_fim("A")
        self.assertFalse(l.inserir_apos("Z", "B"))
        self.assertEqual(l.percorrer(), ["A"])

    def test_remocao_inicio_meio_fim(self):
        l = ListaLigada()
        for e in ["A", "B", "C", "D", "E"]:
            l.inserir_fim(e)
        self.assertEqual(l.remover_inicio(), (True, "A"))   # início
        self.assertTrue(l.remover("C"))                     # meio
        self.assertEqual(l.remover_fim(), (True, "E"))      # fim
        self.assertEqual(l.percorrer(), ["B", "D"])
        self.assertEqual(l.ultimo_elemento(), (True, "D"))  # 'ultimo' foi atualizado

    def test_remover_ultimo_atualiza_ponteiro(self):
        l = ListaLigada()
        l.inserir_fim("A"); l.inserir_fim("B")
        l.remover("B")
        l.inserir_fim("C")
        self.assertEqual(l.percorrer(), ["A", "C"])

    def test_remover_unico(self):
        l = ListaLigada()
        l.inserir_fim("A")
        self.assertTrue(l.remover("A"))
        self.assertTrue(l.esta_vazia())
        self.assertIsNone(l.ultimo)
        l.inserir_fim("B")
        self.assertEqual(l.percorrer(), ["B"])

    def test_busca(self):
        l = ListaLigada()
        for e in ["A", "B", "C"]:
            l.inserir_fim(e)
        self.assertEqual(l.buscar("B").chave, "B")
        self.assertIsNone(l.buscar("Z"))           # elemento inexistente
        self.assertFalse(l.remover("Z"))
        self.assertEqual(len(l), 3)                # nada foi corrompido


class TestAVL(unittest.TestCase):
    def test_exemplo_da_aula(self):
        """Aula 08, slides 9-15: 70, 50, 40, 80, 90, 15, 25, 45, 42."""
        a = ArvoreAVL()
        for k in [70, 50, 40, 80, 90, 15, 25, 45, 42]:
            self.assertTrue(a.inserir(k))
            self.assertTrue(a.eh_avl(), f"deixou de ser AVL após inserir {k}")
        # as 4 rotações, na ordem e nos nós mostrados nos slides
        self.assertEqual(a.historico_rotacoes,
                         [("RD", 70), ("RE", 70), ("RED", 40), ("RDE", 40)])
        # árvore final do slide 15
        r = a.raiz
        self.assertEqual(r.chave, 50)
        self.assertEqual((r.esq.chave, r.dir.chave), (25, 80))
        self.assertEqual((r.esq.esq.chave, r.esq.dir.chave), (15, 42))
        self.assertEqual((r.esq.dir.esq.chave, r.esq.dir.dir.chave), (40, 45))
        self.assertEqual(a.em_ordem(), [15, 25, 40, 42, 45, 50, 70, 80, 90])

    def test_rotacao_direita_isolada(self):
        a = ArvoreAVL()
        for k in [3, 2, 1]:
            a.inserir(k)
        self.assertEqual(a.historico_rotacoes, [("RD", 3)])
        self.assertEqual(a.raiz.chave, 2)
        self.assertEqual(fator_balanceamento(a.raiz), 0)

    def test_rotacao_esquerda_direita_isolada(self):
        a = ArvoreAVL()
        for k in [3, 1, 2]:
            a.inserir(k)
        self.assertEqual(a.historico_rotacoes, [("RED", 3)])
        self.assertEqual(a.raiz.chave, 2)

    def test_chave_duplicada(self):
        a = ArvoreAVL()
        self.assertTrue(a.inserir(10))
        self.assertFalse(a.inserir(10))     # já existe: não insere de novo
        self.assertEqual(len(a), 1)

    def test_busca_existente_e_inexistente(self):
        a = ArvoreAVL()
        for k in range(1, 16):              # inserção em ordem: pior caso de uma BST comum
            a.inserir(k, valor=k * 10)
        self.assertEqual(a.altura(), 3)     # AVL manteve altura mínima (15 nós)
        achou, valor, comparacoes = a.buscar(11)
        self.assertTrue(achou)
        self.assertEqual(valor, 110)
        self.assertLessEqual(comparacoes, 4)
        self.assertEqual(a.buscar(99)[0], False)

    def test_chaves_tupla(self):
        """No jogo a chave é uma tupla (estado); a ordem de tuplas é lexicográfica."""
        a = ArvoreAVL()
        self.assertTrue(a.inserir(("D", ("autenticacao",))))
        self.assertTrue(a.inserir(("D", ())))        # mesma posição, pistas diferentes
        self.assertFalse(a.inserir(("D", ())))
        self.assertEqual(len(a), 2)

    def test_arvore_vazia(self):
        a = ArvoreAVL()
        self.assertEqual(a.altura(), -1)            # aula 07: árvore vazia tem altura -1
        self.assertEqual(a.buscar(1), (False, None, 0))
        self.assertEqual(a.desenhar(), "(árvore vazia)")


if __name__ == "__main__":
    unittest.main()
