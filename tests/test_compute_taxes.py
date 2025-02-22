import unittest

from compute_taxes import TaxBracket, rates, compute_taxes

class TestRatesFunction(unittest.TestCase):
    def test_basic_case_no_capital(self):
        base_income = 50000
        max_convert = 20000
        federal_brackets = [(0.1, 9875), (0.12, 40125), (0.22, 85525)]
        state_brackets = [(0.05, 9875), (0.07, 40125), (0.09, 85525)]
        longterm_brackets = [(0.15, 999990000)]
        nii_brackets = [(0.038, 99999200000)]

        result = rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='split')

        expected = [
            TaxBracket(lower=50000, upper=70000, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0)
        ]

        self.assertEqual(result, expected)

    def test_basic_case_no_capital_multiple_brackets_same_state_federal_brackt(self):
        base_income = 40000
        max_convert = 50000
        federal_brackets = [(0.1, 9875), (0.12, 40125), (0.22, 999999)]
        state_brackets = [(0.05, 9875), (0.07, 40125), (0.09, 999999)]
        longterm_brackets = [(0.15, 999990000)]
        nii_brackets = [(0.038, 99999200000)]

        result = rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='split')

        expected = [
            TaxBracket(lower=40000, upper=40125, state_rate=0.07, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=40125, upper=90000, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0)
        ]

        self.assertEqual(result, expected)

    def test_basic_case_all_brackets(self):
        base_income = 10
        max_convert = 50000
        federal_brackets = [(0.1, 10000), (0.12, 60000), (0.22, 999999)]
        state_brackets = [(0.05, 9875), (0.07, 40125), (0.09, 999999)]
        longterm_brackets = [(0.15, 999990000)]
        nii_brackets = [(0.038, 99999200000)]

        result = rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='split')

        expected = [
            TaxBracket(lower=10, upper=9875, state_rate=0.05, federal_rate=.1, nit=0, longterm=0),
            TaxBracket(lower=9875, upper=10000, state_rate=0.07, federal_rate=0.1, nit=0, longterm=0),
            TaxBracket(lower=10000, upper=40125, state_rate=0.07, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=40125, upper=50010, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
        ]

        self.assertEqual(result, expected)

    def test_basic_case_all_brackets_with_longterm(self):
        base_income = 10
        max_convert = 50000
        federal_brackets = [(0.1, 10000), (0.12, 60000), (0.22, 999999)]
        state_brackets = [(0.05, 9875), (0.07, 40125), (0.09, 999999)]
        longterm_brackets = [(0.0, 50000), (0.15, 999990000)]
        nii_brackets = [(0.0, 100000), (0.038, 99999200000)]


        result = rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='split')

        expected = [
            TaxBracket(lower=10, upper=9875, state_rate=0.05, federal_rate=.1, nit=0, longterm=0),
            TaxBracket(lower=9875, upper=10000, state_rate=0.07, federal_rate=0.1, nit=0, longterm=0),
            TaxBracket(lower=10000, upper=40125, state_rate=0.07, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=40125, upper=50000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=50000, upper=50000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=.15),
            TaxBracket(lower=50000, upper=50010, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
        ]

        self.assertEqual(result, expected)

    def test_basic_case_all_brackets_with_longterm_and_nii(self):
        base_income = 10
        max_convert = 120000
        federal_brackets = [(0.1, 10000), (0.12, 60000), (0.22, 999999)]
        state_brackets = [(0.05, 9875), (0.07, 40125), (0.09, 999999)]
        longterm_brackets = [(0.0, 50000), (0.15, 999990000)]
        nii_brackets = [(0.0, 100000), (0.038, 99999200000)]


        result = rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='split')

        expected = [
            TaxBracket(lower=10, upper=9875, state_rate=0.05, federal_rate=.1, nit=0, longterm=0),
            TaxBracket(lower=9875, upper=10000, state_rate=0.07, federal_rate=0.1, nit=0, longterm=0),
            TaxBracket(lower=10000, upper=40125, state_rate=0.07, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=40125, upper=50000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=50000, upper=50000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=.15),
            TaxBracket(lower=50000, upper=60000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=60000, upper=100000, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0),
            TaxBracket(lower=100000, upper=100000, state_rate=0.09, federal_rate=0.22, nit=.038, longterm=0),
            TaxBracket(lower=100000, upper=120010, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0),
        ]

        self.assertEqual(result, expected)

    def test_basic_case_all_brackets_with_longterm_and_nii_bracket_mode_combine(self):
        base_income = 10
        max_convert = 120000
        federal_brackets = [(0.1, 10000), (0.12, 60000), (0.22, 999999)]
        state_brackets = [(0.05, 9875), (0.07, 40125), (0.09, 999999)]
        longterm_brackets = [(0.0, 50000), (0.15, 999990000)]
        nii_brackets = [(0.0, 100000), (0.038, 99999200000)]

        result = rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='combine')

        expected = [
            TaxBracket(lower=10, upper=9875, state_rate=0.05, federal_rate=.1, nit=0, longterm=0),
            TaxBracket(lower=9875, upper=10000, state_rate=0.07, federal_rate=0.1, nit=0, longterm=0),
            TaxBracket(lower=10000, upper=40125, state_rate=0.07, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=40125, upper=60000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=60000, upper=120010, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0),
            TaxBracket(lower=50000, upper=50000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=.15),
            TaxBracket(lower=100000, upper=100000, state_rate=0.09, federal_rate=0.22, nit=.038, longterm=0),
        ]

class TestComputeTaxes(unittest.TestCase):
    def test_highincome_case(self):
        base_income = 500000
        capital_income = 100000
        investment_income = 200000
        federal_brackets = [(0.1, 9875), (0.12, 40125), (0.22, 85525), (.24, 99999999)]
        state_brackets = [(0.05, 9875), (0.07, 45125), (0.09, 85525), (.11, 999999999)]
        longterm_brackets = [(0, 25000), (0.15, 999990000)]
        nii_brackets = [(0, 250000), (0.038, 99999200000)]

        result = compute_taxes(base_income, capital_income, investment_income, federal_brackets, state_brackets, longterm_brackets, nii_brackets)

        expected_federal = .1 * 9875 + .12 * (40125 - 9875) + .22 * (85525 - 40125) + .24 * (base_income - 85525)
        expected_state = .05 * 9875 + .07 * (45125 - 9875) + .09 * (85525 - 45125) + .11 * (base_income - 85525)
        expected_nii = .038 * investment_income
        expected_longterm = .15 * capital_income

        self.assertEqual(result, (expected_federal, expected_state, expected_nii, expected_longterm))

    def test_mediumincome_case(self):
        base_income = 100000
        capital_income = 10000
        investment_income = 20000
        federal_brackets = [(0.1, 9875), (0.12, 40125), (0.22, 85525), (.24, 99999999)]
        state_brackets = [(0.05, 9875), (0.07, 45125), (0.09, 200000), (.11, 999999999)]
        longterm_brackets = [(0, 25000), (0.15, 200000), (.25, 99999999)]
        nii_brackets = [(0, 250000), (0.038, 99999200000)]

        result = compute_taxes(base_income, capital_income, investment_income, federal_brackets, state_brackets, longterm_brackets, nii_brackets)

        expected_federal = .1 * 9875 + .12 * (40125 - 9875) + .22 * (85525 - 40125) + .24 * (base_income - 85525)
        expected_state = .05 * 9875 + .07 * (45125 - 9875) + .09 * (base_income - 45125)
        expected_nii = 0
        expected_longterm = .15 * capital_income

        self.assertEqual(result, (expected_federal, expected_state, expected_nii, expected_longterm))


if __name__ == '__main__':
    unittest.main()
