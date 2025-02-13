import unittest

from taxes import _initial_rates, _rates, _combine_state_federal_brackets, CombinedTaxBracket, _apply_capital_taxes

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

    def test_apply_capital_taxes(self):
        combined_brackets = [(0.1, 10000), (0.2, 20000), (0.3, 99999999)]
        capital_brackets = [(0, 15000), (.15, 25000), (.2, 99999999)]
        nii_brackets = [(0, 12000), (.1, 9999999)]

        expected = [CombinedTaxBracket(lower=0, upper=10000, income_rate=0.1, marginal_capital=0, marginal_nii=0),
                    CombinedTaxBracket(lower=10000, upper=12000, income_rate=0.2, marginal_capital=0, marginal_nii=0),
                    CombinedTaxBracket(lower=12000, upper=12000, income_rate=0.2, marginal_capital=0, marginal_nii=.1),
                    CombinedTaxBracket(lower=12000, upper=15000, income_rate=0.2, marginal_capital=.15, marginal_nii=0),
                    CombinedTaxBracket(lower=15000, upper=20000, income_rate=0.3, marginal_capital=0, marginal_nii=0),
                    CombinedTaxBracket(lower=20000, upper=25000, income_rate=0.3, marginal_capital=.05, marginal_nii=0),
                    CombinedTaxBracket(lower=25000, upper=99999999, income_rate=0.3, marginal_capital=0, marginal_nii=0)]

        actual = _apply_capital_taxes(combined_brackets, capital_brackets, nii_brackets)
        for e, a in zip(expected, actual):
            self.assertAlmostEqual(e.income_rate, a.income_rate)
            self.assertAlmostEqual(e.marginal_capital, a.marginal_capital)
            self.assertAlmostEqual(e.marginal_nii, a.marginal_nii)
            self.assertEqual(e.lower, a.lower)
            self.assertEqual(e.upper, a.upper)



if __name__ == '__main__':
    unittest.main()
