import unittest

from src.quant import Addition, Symbol

class TestAddition(unittest.TestCase):
    def test_addition_print(self):
        a = Symbol('a')
        b = Symbol('b')

        self.assertEqual(repr(Addition(a, b)), '(a + b)')
        self.assertEqual(repr(-Addition(a, b)), '-(a + b)')
    
    def test_addition_inline_addition(self):
        a = Symbol('a')
        b = Symbol('b')

        self.assertEqual(repr(a + b), '(a + b)')

    def test_addition_neg_rhs(self):
        a = Symbol('a')
        b = Symbol('b')

        self.assertEqual(repr(a + (-b)), '(a - b)')
        self.assertEqual(repr(a - b), '(a - b)')

    def test_addition_neg_lhs(self):
        a = Symbol('a')
        b = Symbol('b')

        self.assertEqual(repr(-a + b), '(-a + b)')

    def test_addition_both_neg(self):
        a = Symbol('a')
        b = Symbol('b')

        self.assertEqual(repr(-a - b), '-(a + b)')
        self.assertEqual(repr(-(-a - b)), '(a + b)')


if __name__ == '__main__':
    unittest.main()