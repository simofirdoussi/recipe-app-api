

from django.test import SimpleTestCase
from . import calc


class CalculatorTest(SimpleTestCase):

    def test_calc_add(self):
        """ Test adding numbers. """
        resu = calc.add(5, 9)
        self.assertEqual(resu, 14)

    def test_calc_substract(self):
        """ Test subtracting numbers. """
        resu = calc.substract(35, 25)
        self.assertEqual(resu, 10)
