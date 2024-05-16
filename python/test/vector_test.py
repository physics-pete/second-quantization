import unittest

from src.quant import Ket, Symbol, FermionKet, FermionBra, Integer


class TestKet(unittest.TestCase):
    def test_ket_none(self):
        ket = Ket()
        self.assertEqual(repr(ket), '|⟩')

    def test_ket_single_state(self):
        a = Symbol('a')
        ket = Ket((a, ))
        self.assertEqual(repr(ket), '|a⟩')

    def test_ket_multi_state(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = Ket((a, b))
        self.assertEqual(repr(ket), '|a, b⟩')

    def test_ket_double_state(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = Ket({a: 2, b: 1})
        self.assertEqual(repr(ket), '|a:2, b⟩')

        ket = Ket({b: 1, a: 3})
        self.assertEqual(repr(ket), '|b, a:3⟩')

class TestFermionKet(unittest.TestCase):
    def test_fket_init(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = FermionKet(a, b)
        self.assertEqual(repr(ket), '|a, b⟩')

    def test_fket_create(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = FermionKet(a)
        self.assertEqual(repr(ket.create(b)), '-|a, b⟩')

    def test_fket_annihilate_unkown_state(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = FermionKet(a)
        self.assertEqual(repr(ket.annihilate(b)), '0')
    
    def test_fket_annihilate(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        ket = FermionKet(a, b, c)
        self.assertEqual(repr(ket.annihilate(Symbol('b'))), '-|a, c⟩')

    def test_fket_inner(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = FermionKet(a, b)
        bra = FermionBra(a, b)
        self.assertEqual(bra.inner(ket), Integer.ONE())

    def test_fket_inner_not_equal(self):
        a = Symbol('a')
        b = Symbol('b')
        ket = FermionKet(a, b)
        bra = FermionBra()
        self.assertEqual(bra.inner(ket), Integer.ZERO())

if __name__ == '__main__':
    unittest.main()