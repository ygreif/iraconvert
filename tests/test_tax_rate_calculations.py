import unittest

from taxes import _initial_rates, _rates, _combine_state_federal_brackets

class TestTaxCalculations(unittest.TestCase):

    def test_initial_rates(self):
        brackets = [(0.1, 10000), (0.2, 20000), (0.3, 30000)]
        self.assertEqual(_initial_rates(5000, brackets), (0.1, 10000))
        self.assertEqual(_initial_rates(15000, brackets), (0.2, 20000))
        self.assertEqual(_initial_rates(25000, brackets), (0.3, 30000))
        self.assertIsNone(_initial_rates(35000, brackets))

    def test_combine_state_federal_brackets(self):
        federal = [(0.1, 10000), (0.2, 20000), (0.3, 99999999)]
        state = [(0.05, 5000), (0.06, 9999999)]

        expected = [(0.15, 5000), (0.16, 10000), (0.26, 20000), (0.36, 9999999)]
        actual = _combine_state_federal_brackets(federal, state)

        for e, a in zip(expected, actual):
            self.assertAlmostEqual(e[0], a[0])
            self.assertEqual(e[1], a[1])

    def test_rates(self):
        brackets = [(0.1, 10000), (0.2, 20000), (0.3, 99999999)]
        self.assertEqual(_rates(5000, 1000, brackets), [( (5000, 6000), .1  )]       )
        self.assertEqual(_rates(5000, 6000, brackets), [( (5000, 10000), .1  ), ((10000, 11000), .2  )]       )
        self.assertEqual(_rates(5000, 40000, brackets), [( (5000, 10000), .1  ), ((10000, 20000), .2  ), ((20000, 45000), .3  )]       )

if __name__ == '__main__':
    unittest.main()
