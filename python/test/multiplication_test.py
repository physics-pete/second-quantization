import unittest

from src.quant import Multiplication, Symbol, FermionKet, Integer

a = Symbol("a")
b = Symbol("b")

ab = '[a⋅b]'
neg_ab = '-[a⋅b]'

class TestMultiplication(unittest.TestCase):
    def test_multiply(self):
        m = Multiplication(a, b)
        self.assertEqual(repr(m), ab)

    def test_multiply_inline(self):
        m = a * b
        self.assertEqual(repr(m), ab)

    def test_multiply_signs(self):
        self.assertEqual(repr((-a) * b), neg_ab)
        self.assertEqual(repr(a * (-b)), neg_ab)
        self.assertEqual(repr((-a) * (-b)), ab)
        self.assertEqual(repr(-((-a) * (-b))), neg_ab)
        self.assertEqual(repr(-((-a) * b)), ab)
        self.assertEqual(repr(-(a * (-b))), ab)

    def test_multiply_ket_symbol(self):
        self.assertEqual(repr(FermionKet(b) * a), '[a⋅|b⟩]')

    def test_multiply_symbol_number(self):
        number = Integer(3)
        self.assertEqual(repr(number * a), '[3⋅a]', 'Normal order')
        self.assertEqual(repr(a * number), '[3⋅a]', 'reverse Order')

if __name__ == '__main__':
    unittest.main()