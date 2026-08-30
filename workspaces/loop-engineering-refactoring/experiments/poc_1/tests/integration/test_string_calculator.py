import unittest
import sys
import os

# Add src to sys.path to import domain
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from domain.string_calculator import StringCalculator

class TestStringCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.calc = StringCalculator()

    def test_empty_string_returns_zero(self) -> None:
        self.assertEqual(self.calc.add(""), 0)

    def test_single_number_returns_value(self) -> None:
        self.assertEqual(self.calc.add("1"), 1)

    def test_two_numbers_returns_sum(self) -> None:
        self.assertEqual(self.calc.add("1,2"), 3)

    def test_multiple_numbers_returns_sum(self) -> None:
        self.assertEqual(self.calc.add("1,2,3,4"), 10)

if __name__ == '__main__':
    unittest.main()
