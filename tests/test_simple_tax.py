import unittest

import simple_taxes

class TestTaxSchedule(unittest.TestCase):

    def setUp(self):
        self.pretax_wage_income = 50000
        self.ordinary_capital_income = 10000
        self.qualified_capital_income = 5000
        self.federal_brackets = [(0.1, 9875), (0.12, 40125), (0.22, 85525), (.3, 99999999)]
        self.state_brackets = [(0.03, 9875), (0.05, 40125), (0.07, 999999999)]
        self.nit_brackets = [(0, 100000), (0.2, 99999999)]
        self.longterm_brackets = [(0, 56000), (0.15, 100000), (0.2, 99999999)]
        self.federal_deduction = 12000
        self.state_deduction = 5000

        self.tax_schedule = simple_taxes.TaxSchedule(
            self.pretax_wage_income,
            self.ordinary_capital_income,
            self.qualified_capital_income,
            self.federal_brackets,
            self.state_brackets,
            self.nit_brackets,
            self.longterm_brackets,
            self.federal_deduction,
            self.state_deduction
        )

    def test_apply_income_tax(self):
        income = 50000
        brackets = [(0.1, 9875), (0.12, 40125), (0.22, 85525)]
        expected_tax = .1 * 9875 + .12 * (40125 - 9875) + .22 * (50000 - 40125)
        self.assertAlmostEqual(self.tax_schedule.apply_income_tax(income, brackets), expected_tax)

    def test_apply_capital_tax(self):
        capital_income = 5000
        bracket_income = 45000
        brackets = [(0.1, 40000), (0.2, 80000)]
        expected_tax = 1000
        self.assertAlmostEqual(self.tax_schedule.apply_capital_tax(capital_income, bracket_income, brackets), expected_tax)

    def test_ordinary_income(self):
        self.assertEqual(self.tax_schedule.ordinary_income(), self.pretax_wage_income + self.ordinary_capital_income - self.federal_deduction)

    def test_state_tax(self):
        conversion_amount = 10000
        adjusted_state_income = self.pretax_wage_income + self.ordinary_capital_income + self.qualified_capital_income - self.state_deduction + conversion_amount
        expected_tax = .03 * 9875 + .05 * (40125 - 9875) + .07 * (adjusted_state_income - 40125)
        self.assertAlmostEqual(self.tax_schedule.state_tax(conversion_amount), expected_tax)


    def test_federal_tax(self):
        conversion_amount = 10000
        expected_tax = 6797.5

        ordinary_income = self.pretax_wage_income + self.ordinary_capital_income + conversion_amount - self.federal_deduction
        expected_tax = .1 * 9875 + .12 * (40125 - 9875) + .22 * (ordinary_income - 40125)
        self.assertAlmostEqual(self.tax_schedule.federal_tax(conversion_amount), expected_tax)

    def test_federal_tax_high(self):
        conversion_amount = 100000
        expected_tax = 6797.5

        ordinary_income = self.pretax_wage_income + self.ordinary_capital_income + conversion_amount - self.federal_deduction
        expected_tax = .1 * 9875 + .12 * (40125 - 9875) + .22 * (85525 - 40125) + .3 * (ordinary_income - 85525)
        self.assertAlmostEqual(self.tax_schedule.federal_tax(conversion_amount), expected_tax)

    def test_no_nit_tax(self):
        conversion_amount = 10000
        expected_tax = 0
        self.assertAlmostEqual(self.tax_schedule.nit_tax(conversion_amount), expected_tax)

    def test_has_nit_tax(self):
        conversion_amount = 55000
        expected_tax = .2 * (self.ordinary_capital_income + self.qualified_capital_income)
        self.assertAlmostEqual(self.tax_schedule.nit_tax(conversion_amount), expected_tax)

    def test_low_longterm_tax(self):
        conversion_amount = 0
        expected_tax = 0
        self.assertAlmostEqual(self.tax_schedule.longterm_tax(conversion_amount), expected_tax)

    def test_medium_longterm_tax(self):
        conversion_amount = 40000
        expected_tax = .15 * self.qualified_capital_income
        self.assertAlmostEqual(self.tax_schedule.longterm_tax(conversion_amount), expected_tax)

    def test_high_longterm_tax(self):
        conversion_amount = 100000
        expected_tax = .2 * self.qualified_capital_income
        self.assertAlmostEqual(self.tax_schedule.longterm_tax(conversion_amount), expected_tax)

    def assertTupleAlmostEqual(self, tuple1, tuple2, places=7):
        """Custom assertion for tuples with floating-point values."""
        self.assertEqual(len(tuple1), len(tuple2), "Tuples must have the same length")
        for a, b in zip(tuple1, tuple2):
            self.assertAlmostEqual(a, b, places=places)

    def test_rate_at_income(self):
        brackets = [(0.1, 9875), (0.12, 40125), (0.25, 85525)]
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(0, brackets), (0.1, .1))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(9875, brackets), (0.12, .12))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(40125, brackets), (0.25, .25))

    def test_rate_at_nit(self):
        brackets = [(0, 100000), (0.2, 99999999)]
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(0, brackets, is_capital=True), (0, 0))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(100000, brackets, is_capital=True), (0.2, 0.2))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(200000, brackets, is_capital=True), (0.2, 0.0))

    def test_rate_at_longterm(self):
        brackets = [(0, 100000), (0.15, 200000), (.2, 99999999)]
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(50000, brackets, is_capital=True), (0, 0))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(100000, brackets, is_capital=True), (0.15, 0.15))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(150000, brackets, is_capital=True), (0.15, 0.0))
        self.assertTupleAlmostEqual(self.tax_schedule.rate_at(200000, brackets, is_capital=True), (0.2, 0.05))

    def test_keypoints(self):
        brackets = [(0.1, 9875), (0.12, 40125), (0.22, 50000), (0.3, 99999999)]
        self.assertEqual(self.tax_schedule._keypoints(0, brackets, 45000), [9875, 40125])
        self.assertEqual(self.tax_schedule._keypoints(40000, brackets, 100000), [125, 10000])

    def test_construct_income_keypoints(self):
        max_conversion_amount = 50000
        #expected_keypoints = {0, 9875, 40125, 50000, 140000}
        #import pdb;pdb.set_trace()
        #federal_base_income = self.pretax_wage_income + self.ordinary_capital_income - self.federal_deduction # 48000
        #expcted_federal_keypoints = [85525 - 48000, 50000]

        #base_state_income = self.pretax_wage_income + self.ordinary_capital_income + self.qualified_capital_income - self.state_deduction # 55000
        #expected_state_keypoints = [99999 - 55000]

        expected_keypoints = [0, 85525 - 48000, 50000]
        self.assertEqual(self.tax_schedule._construct_income_keypoints(max_conversion_amount), expected_keypoints)

    def test_construct_capital_keypoints(self):
        max_conversion_amount = 50000
        expected_keypoints = [8000]
        self.assertEqual(self.tax_schedule._construct_capital_keypoints(max_conversion_amount), expected_keypoints)

    def test__construct_bracket_from_two_points(self):
        result = self.tax_schedule._construct_bracket_from_two_points(37525, 100000)
        expected = simple_taxes.TaxBracket(
            lower=37525,
            upper=100000,

            state=simple_taxes.TaxBundle(rate=.07, marginal=.07, amount=self.tax_schedule.state_tax(100000)),
            federal=simple_taxes.TaxBundle(rate=.3, marginal=.3, amount=self.tax_schedule.federal_tax(100000)),
            nit=simple_taxes.TaxBundle(rate=.2, marginal=0, amount=self.tax_schedule.nit_tax(100000)),
            longterm=simple_taxes.TaxBundle(rate=.2, marginal=0, amount=self.tax_schedule.longterm_tax(100000))
        )
        self.assertEqual(result.lower, expected.lower)
        self.assertEqual(result.upper, expected.upper)

        self.assertAlmostEqual(result.state.rate, expected.state.rate)
        self.assertAlmostEqual(result.state.marginal, expected.state.marginal)
        self.assertAlmostEqual(result.state.amount, expected.state.amount)

        self.assertAlmostEqual(result.federal.amount, expected.federal.amount)
        self.assertAlmostEqual(result.federal.rate, expected.federal.rate)
        self.assertAlmostEqual(result.federal.marginal, expected.federal.marginal)

        self.assertAlmostEqual(result.nit.rate, expected.nit.rate)
        self.assertAlmostEqual(result.nit.marginal, expected.nit.marginal)
        self.assertAlmostEqual(result.nit.amount, expected.nit.amount)

    def test__construct_bracket_from_one_point(self):
        result = self.tax_schedule._construct_bracket_from_one_point(52000)
        expected = simple_taxes.TaxBracket(
            lower=52000,
            upper=52000,

            state=simple_taxes.TaxBundle(rate=.07, marginal=.07, amount=self.tax_schedule.state_tax(52000)),
            federal=simple_taxes.TaxBundle(rate=.3, marginal=.3, amount=self.tax_schedule.federal_tax(52000)),
            nit=simple_taxes.TaxBundle(rate=.2, marginal=.2, amount=self.tax_schedule.nit_tax(52000)),
            longterm=simple_taxes.TaxBundle(rate=.2, marginal=0, amount=self.tax_schedule.longterm_tax(52000))
        )
        self.assertEqual(result.lower, expected.lower)
        self.assertEqual(result.upper, expected.upper)

        self.assertAlmostEqual(result.nit.rate, expected.nit.rate)
        self.assertAlmostEqual(result.nit.marginal, expected.nit.marginal)
        self.assertAlmostEqual(result.nit.amount, expected.nit.amount)

        self.assertAlmostEqual(result.longterm.marginal, .05)

    def test_tax_curve(self):
        max_conversion_amount = 100000
        entire_schedule = simple_taxes.TaxSchedule(
            10000,
            self.ordinary_capital_income,
            0,
            self.federal_brackets,
            [(.01, 10000), (.11, 250000), (.2, 99999999)],
            self.nit_brackets,
            self.longterm_brackets,
            self.federal_deduction,
            self.federal_deduction
        )
        income_curve, capital_taxes, entire_curve = entire_schedule.tax_curve(max_conversion_amount)

        self.assertEqual(len(capital_taxes), 2)
        self.assertEqual(capital_taxes[0].lower, 48000)
        self.assertEqual(capital_taxes[0].upper, 48000)
        self.assertEqual(capital_taxes[0].nit.rate, 0)
        self.assertEqual(capital_taxes[0].longterm.rate, .15)
        self.assertEqual(capital_taxes[0].longterm.marginal, .15)

        self.assertAlmostEqual(capital_taxes[1].lower, 92000)
        self.assertAlmostEqual(capital_taxes[1].upper, 92000)
        self.assertAlmostEqual(capital_taxes[1].nit.rate, .2)
        self.assertAlmostEqual(capital_taxes[1].nit.marginal, .2)
        self.assertAlmostEqual(capital_taxes[1].longterm.rate, .2)
        self.assertAlmostEqual(capital_taxes[1].longterm.marginal, .05)

        self.assertEqual(len(income_curve), 5)

        self.assertEqual(income_curve[0].lower, 0)
        self.assertEqual(income_curve[0].upper, 1875)
        self.assertAlmostEqual(income_curve[0].state.rate, .01)
        self.assertAlmostEquals(income_curve[0].federal.rate, .1)
        self.assertEqual(income_curve[0].nit.rate, 0)
        self.assertEqual(income_curve[0].longterm.rate, 0)

        self.assertEqual(income_curve[1].lower, 1875)
        self.assertEqual(income_curve[1].upper, 2000)
        self.assertAlmostEqual(income_curve[1].state.rate, .01)
        self.assertAlmostEquals(income_curve[1].federal.rate, .12)
        self.assertEqual(income_curve[1].nit.rate, 0)
        self.assertEqual(income_curve[1].longterm.rate, 0)

        self.assertEqual(income_curve[2].lower, 2000)
        self.assertEqual(income_curve[2].upper, 32125)
        self.assertAlmostEqual(income_curve[2].state.rate, .11)
        self.assertAlmostEquals(income_curve[2].federal.rate, .12)
        self.assertEqual(income_curve[2].nit.rate, 0)
        self.assertEqual(income_curve[2].longterm.rate, 0)

        self.assertEqual(income_curve[3].lower, 32125)
        self.assertEqual(income_curve[3].upper, 85525 - 8000)
        self.assertAlmostEqual(income_curve[3].state.rate, .11)
        self.assertAlmostEquals(income_curve[3].federal.rate, .22)
        self.assertEqual(income_curve[3].nit.rate, 0)
        self.assertEqual(income_curve[3].longterm.rate, .15)
        self.assertAlmostEquals(income_curve[3].longterm.marginal, 0)

        self.assertEqual(income_curve[4].lower, 85525 - 8000)
        self.assertEqual(income_curve[4].upper, max_conversion_amount)
        self.assertAlmostEqual(income_curve[4].state.rate, .11)
        self.assertAlmostEquals(income_curve[4].federal.rate, .3)
        self.assertEqual(income_curve[4].nit.rate, .2)
        self.assertEqual(income_curve[4].longterm.rate, .2)
        self.assertAlmostEquals(income_curve[4].longterm.marginal, 0)
        self.assertAlmostEquals(income_curve[4].nit.marginal, 0)

        self.assertEqual(len(entire_curve), 7)
        self.assertEqual(entire_curve[0], income_curve[0])
        self.assertEqual(entire_curve[1], income_curve[1])
        self.assertEqual(entire_curve[2], income_curve[2])

        self.assertEqual(entire_curve[3].lower, 32125)
        self.assertEqual(entire_curve[3].upper, 48000)
        self.assertAlmostEqual(entire_curve[3].state.rate, .11)
        self.assertAlmostEquals(entire_curve[3].federal.rate, .22)
        self.assertEqual(entire_curve[3].nit.rate, 0)
        self.assertEqual(entire_curve[3].longterm.rate, .15)

        self.assertEqual(entire_curve[4].lower, 48000)
        self.assertEqual(entire_curve[4].upper, 85525 - 8000)

        self.assertEqual(entire_curve[5].lower, 85525 - 8000)
        self.assertEqual(entire_curve[5].upper, 92000)

        self.assertEqual(entire_curve[6].lower, 92000)
        self.assertEqual(entire_curve[6].upper, max_conversion_amount)



















if __name__ == '__main__':
    unittest.main()
