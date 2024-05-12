import unittest

from src.quant import (
  Integer
)

class TestInteger(unittest.TestCase):
    def test_integer_print(self):
        self.assertEqual(repr(Integer(4)), '4')
        self.assertEqual(repr(-Integer(4)), '-4')
    
    def test_integer_addition(self):
        self.assertEqual(Integer(1) + Integer(2), Integer(3))

    def test_integer_subtraction(self):
        self.assertEqual(Integer(1) - Integer(2), -Integer(1))
        self.assertEqual(Integer(1) - Integer(2), -Integer(1))

    def test_integer_multiplication(self):
        self.assertEqual(Integer(5) * Integer(2), Integer(10))
        self.assertEqual(-Integer(5) * Integer(2), -Integer(10))

if __name__ == '__main__':
    unittest.main()