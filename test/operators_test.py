import unittest

from src.quant import (
    FermionCreation, 
    FermionAnnihilation, 
    Symbol, 
    FermionKet,
    FermionBra,
    Integer
)

a = Symbol("a")
b = Symbol("b")
c = Symbol("c")

class TestOperator(unittest.TestCase):
    def test_operator_creation(self):
        c = FermionCreation(a)
        self.assertEqual(repr(c), "c_a†")

    def test_operator_annihiliation(self):
        c = FermionAnnihilation(a)
        self.assertEqual(repr(c), "c_a")

    def test_operator_annihilation_dagger(self):
        c = FermionAnnihilation(a).dagger()
        self.assertIsInstance(c, FermionCreation)

    def test_operator_creation_dagger(self):
        c = FermionCreation(a).dagger()
        self.assertIsInstance(c, FermionAnnihilation)

    def test_operator_apply_creation_ket(self):
        c = FermionCreation(a)
        s = FermionKet(b)
        self.assertEqual(c.apply(s), FermionKet(a, b))

    def test_operator_apply_annihilation_ket(self):
        c = FermionAnnihilation(a)
        s = FermionKet(a)
        self.assertEqual(c.apply(s), FermionKet())

    def test_operator_apply_creation_bra(self):
        c = FermionCreation(a)
        s = FermionBra(a)
        self.assertEqual(c.apply(s), FermionBra())

    def test_operator_apply_annihilation_bra(self):
        c = FermionAnnihilation(a)
        s = FermionBra(b)
        self.assertEqual(c.apply(s), FermionBra(a,b))

    def test_operator_some_term(self):
        cc = FermionCreation(a)
        ca = FermionAnnihilation(a)
        B = FermionBra(b)
        K = FermionKet(b)
        self.assertEqual(repr(B * c * cc * ca * K), "[[[[c⋅⟨b|]⋅c_a†]⋅c_a]⋅|b⟩]")


if __name__ == '__main__':
    unittest.main()