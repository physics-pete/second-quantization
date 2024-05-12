import unittest

from src.quant import (
    Integer, 
    Symbol, 
    FermionKet, 
    FermionCreation, 
    FermionAnnihilation, 
    FermionBra, 
    expand,
    simplify
    )

a = Symbol("a")
b = Symbol("b")
c = Symbol("c")
d = Symbol("d")

class TestSimplify(unittest.TestCase):
    def test_simplify_complex_term_zero(self):
        ac = FermionCreation(a)
        aa = FermionAnnihilation(a)
        B = FermionBra(c)
        K = FermionKet(c)

        H = Integer(2) * b * ac * aa

        expanded_term = expand(B * H * K)
        
        self.assertEqual(
            repr(simplify(expanded_term)), 
            "0"
            )
        
    def test_simplify_complex_term_not_zero(self):
        ac = FermionCreation(a)
        aa = FermionAnnihilation(a)
        B = FermionBra(a)
        K = FermionKet(a)

        H = Integer(2) * b * ac * aa

        expanded_term = expand(B * H * K)
        
        self.assertEqual(
            repr(simplify(expanded_term)), 
            "[2⋅b]"
            )


if __name__ == '__main__':
    unittest.main()
