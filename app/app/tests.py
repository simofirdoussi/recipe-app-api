

from django.test import SimpleTestCase
from .calc import calculator

class CalculatorTest(SimpleTestCase):

    def test_calc(self):

        resu = calculator(5,9)

        self.assertEqual(resu, 14)