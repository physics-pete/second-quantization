import unittest

from src.quant import Integer, Symbol, FermionKet, FermionCreation, FermionAnnihilation, FermionBra, expand

a = Symbol("a")
b = Symbol("b")
c = Symbol("c")
d = Symbol("d")

class TestExpand(unittest.TestCase):
    def test_expand_multiply_rhs(self):
        r = a * (b + c)
        self.assertEqual(repr(r.expand()), '([a⋅b] + [a⋅c])')

    def test_expand_multiply_lhs(self):
        r = (a + b) * c
        self.assertEqual(repr(r.expand()), '([a⋅c] + [b⋅c])')

    def test_expand_multiply_rhs_signs(self):
        r = (-a) * (b + c)
        self.assertEqual(repr(r.expand()), '-([a⋅b] + [a⋅c])')
        r = (-a) * (-b + c)
        self.assertEqual(repr(r.expand()), '([a⋅b] - [a⋅c])')
        r = (-a) * (b - c)
        self.assertEqual(repr(r.expand()), '(-[a⋅b] + [a⋅c])')
        r = (-a) * (-b - c)
        self.assertEqual(repr(r.expand()), '([a⋅b] + [a⋅c])')
        r = a * (-b + c)
        self.assertEqual(repr(r.expand()), '(-[a⋅b] + [a⋅c])')
        r = a * (b - c)
        self.assertEqual(repr(r.expand()), '([a⋅b] - [a⋅c])')
        r = a * (-b - c)
        self.assertEqual(repr(r.expand()), '-([a⋅b] + [a⋅c])')

    def test_expand_product_state(self):
        d = Symbol('d')
        r = a * (FermionKet(b) + FermionKet(c) + FermionKet(d))
        self.assertEqual(repr(r.expand()), '([a⋅(|b⟩ + |c⟩)] + [a⋅|d⟩])')

    def test_expand_complex_term(self):
        cc = FermionCreation(a)
        ca = FermionAnnihilation(a)
        B = FermionBra(b)
        K = FermionKet(b)
        self.assertEqual(repr(expand(B * c * cc * ca * K)), "[c⋅[⟨b|⋅[c_a†⋅[c_a⋅|b⟩]]]]")

    def test_expand_complex_term2(self):
        ac = FermionCreation(a)
        aa = FermionAnnihilation(a)
        bc = FermionCreation(b)
        ba = FermionAnnihilation(b)
        B = FermionBra(c)
        K = FermionKet(c)

        H = (Integer(2) * b * ac * aa + d * bc * ba)

        self.assertEqual(
            repr(expand(B * H * K)), 
            "([2⋅[b⋅[⟨c|⋅[c_a†⋅[c_a⋅|c⟩]]]]] + [d⋅[⟨c|⋅[c_b†⋅[c_b⋅|c⟩]]]])"
            )

if __name__ == '__main__':
    unittest.main()
