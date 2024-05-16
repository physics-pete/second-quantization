import unittest

from src.quant import Integer


class TestInteger(unittest.TestCase):
    def test_integer(self):
        a = Integer(2)
        b = Integer(3)
        r = a + b
        self.assertEqual(repr(r.simplify()), '5')

if __name__ == '__main__':
    unittest.main()