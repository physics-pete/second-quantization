import unittest

from src.quant import Sign

class TestSign(unittest.TestCase):
    def test_sign_print(self):
        self.assertEqual(repr(Sign.POSITIVE), '')
        self.assertEqual(str(Sign.POSITIVE), '')
        self.assertEqual(repr(Sign.NEGATIVE), '-')
        self.assertEqual(str(Sign.NEGATIVE), '-')
    
    def test_sign_negation(self):
        self.assertEqual(-Sign.POSITIVE, Sign.NEGATIVE)
        self.assertEqual(-Sign.NEGATIVE, Sign.POSITIVE)

    def test_sign_multiplication(self):
        self.assertEqual(Sign.NEGATIVE * Sign.NEGATIVE, Sign.POSITIVE)
        self.assertEqual(Sign.POSITIVE * Sign.NEGATIVE, Sign.NEGATIVE)
        self.assertEqual(Sign.NEGATIVE * Sign.POSITIVE, Sign.NEGATIVE)
        self.assertEqual(Sign.POSITIVE * Sign.POSITIVE, Sign.POSITIVE)


if __name__ == '__main__':
    unittest.main()