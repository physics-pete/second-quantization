import unittest

from src.quant import Symbol

class TestSymbol(unittest.TestCase):
    def test_symbol_print(self):
        a = Symbol('a')
        self.assertEqual(repr(a), 'a')

    
    def test_symbol_negation(self):
        a = Symbol('a')
        self.assertEqual(repr(-a), '-a')

    def test_symbol_ordering(self):
        a = Symbol('a')
        b = Symbol('b')

        self.assertEqual(min(b, a), a)


if __name__ == '__main__':
    unittest.main()