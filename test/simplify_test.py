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
    
    def test_simplify_complex_term_negative_sign_before_addition(self):
        ac = FermionCreation(a)
        B = FermionBra(a)
        K = FermionKet()


        expanded_term = expand(-(Integer(0) + b * (B * (ac * K))))
        
        self.assertEqual(
            repr(expanded_term.simplify()), 
            "-[b⋅[⟨a|⋅[c_a†⋅|⟩]]]"
            )


if __name__ == '__main__':
    unittest.main()
