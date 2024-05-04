import unittest

from src.quant import (
  FermionKet,
  FermionBra,
  Symbol, 
  Fd, 
  F, 
  full_simplify, 
  full_expand, 
  ONE
)

class TestState(unittest.TestCase):
    a = Symbol('a')
    b = Symbol('b')

    def test_destroy(self):
        psi = FermionKet(self.a)
        op = F(self.a)
        self.assertEqual(FermionKet(), op.apply(psi))

    def test_create(self):
        psi = FermionKet()
        op = Fd(self.a)
        self.assertEqual(FermionKet(self.a), op.apply(psi))

    def test_number_operator(self):
        psi = FermionKet(self.a)
        op = Fd(self.a) * F(self.a)
        self.assertEqual(psi, full_simplify(full_expand(op * psi)))

    def test_add_state(self):
        psi1 = FermionKet(self.a)
        psi2 = FermionKet(self.b)

        op_b = Fd(self.b)
        op_a = Fd(self.a)

        self.assertEqual(
            FermionKet(self.a, self.b), 
            op_a.apply(psi2)
        )

        self.assertEqual(
            -FermionKet(self.a, self.b), 
            op_b.apply(psi1)
        )
    def test_hermitian(self):
        psi1 = FermionKet(self.a)
        psi2 = FermionBra(self.b)

        op1 = Fd(self.b) * F(self.a)
        op2 = Fd(self.a) * F(self.b)

        self.assertEqual(ONE, full_simplify(full_expand(psi2 * op1 * psi1)))
        self.assertEqual(ONE, full_simplify(full_expand(psi1.dagger() * op2 * psi2.dagger())))

    def test_two_particle_state_hermitian(self):
        c = Symbol('c')

        psi1 = FermionKet(self.a, self.b)
        psi2 = FermionBra(c, self.b)

        op1 = Fd(c) * F(self.a)
        op2 = Fd(self.a) * F(c)

        self.assertEqual(ONE, full_simplify(full_expand(psi2 * op1 * psi1)))
        self.assertEqual(ONE, full_simplify(full_expand(psi1.dagger() * op2 * psi2.dagger())))

if __name__ == '__main__':
    unittest.main()