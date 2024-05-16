import sys
import os
sys.path.append(os.getcwd())

import unittest
from src.quant import (
  full_summarize,
  Symbol,
  Integer,
  ZERO
)

class TestSummerize(unittest.TestCase):
    def test_summerize_symbols(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')

        self.assertEqual(repr(full_summarize(a * b + a * c)), repr(a * (b + c)))

    def test_summerize_similar_symbols(self):
        a = Symbol('a')

        self.assertEqual(repr(full_summarize(a + a)), repr(Integer(2) * a))
        self.assertEqual(repr(full_summarize(a - a)), repr(ZERO))

    def test_summerize_multiple_termns(self):
        a = Symbol('a')

        self.assertEqual(repr(full_summarize(a + a + a)), repr(Integer(3) * a))
        self.assertEqual(repr(full_summarize(a + a + a + a)), repr(Integer(4) * a))

if __name__ == '__main__':
    unittest.main()