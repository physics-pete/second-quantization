import unittest

from .addition_test import TestAddition
from .multiplication_test import TestMultiplication
from .sign_test import TestSign
from .symbol_test import TestSymbol
from .expand_test import TestExpand
from .vector_test import TestFermionKet, TestKet

if __name__ == '__main__':
    unittest.main()