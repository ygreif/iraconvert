from dataclasses import dataclass
from collections import namedtuple

@dataclass
class TaxBundle:
    rate: float
    marginal: float

    amount: float

@dataclass
class TaxBracket:
    lower: float
    upper: float

    state: TaxBundle
    federal: TaxBundle
    nit: TaxBundle
    longterm: TaxBundle

    def total_tax(self):
        return self.state.amount + self.federal.amount + self.nit.amount + self.longterm.amount

    def total_capital_tax(self):
        return self.nit.amount + self.longterm.amount

    def total_income_tax(self):
        return self.federal.rate + self.state.rate


class TaxSchedule:
    # brackets are of the form (rate, upper_bound)
    def __init__(self, pretax_wage_income, ordinary_capital_income, qualified_capital_income, federal_brackets, state_brackets, nit_brackets, longterm_brackets, federal_deduction, state_deduction):
        self.pretax_wage_income = pretax_wage_income
        self.ordinary_capital_income = ordinary_capital_income
        self.qualified_capital_income = qualified_capital_income
        self.federal_brackets = federal_brackets
        self.state_brackets = state_brackets
        self.nit_brackets = nit_brackets
        self.longterm_brackets = longterm_brackets

        self.federal_deduction = federal_deduction
        self.state_deduction = state_deduction

        self.initial_tax = self._construct_bracket_from_one_point(0)

    def additional_tax(self, conversion_amount):
        new_tax = self._construct_bracket_from_one_point(conversion_amount)
        return new_tax.total_tax() - self.initial_tax.total_tax()

    def _construct_bracket_from_one_point(self, conversion_amount):
        return self._construct_bracket_from_two_points(conversion_amount, conversion_amount)

    def _construct_bracket_from_two_points(self, conversion_amount, conversion_amount2):
        state_rate, state_marginal = self.rate_at(self.state_income() +  conversion_amount, self.state_brackets)
        federal_rate, federal_marginal = self.rate_at(self.ordinary_income() + conversion_amount, self.federal_brackets)
        nit_rate, nit_marginal = self.rate_at(self._income_for_capital_brackets() + conversion_amount2, self.nit_brackets, is_capital=True)
        longterm_rate, longterm_marginal = self.rate_at(self._income_for_capital_brackets() + conversion_amount2, self.longterm_brackets, is_capital=True)

        state_tax = self.state_tax(conversion_amount2)
        federal_tax = self.federal_tax(conversion_amount2)
        nit_tax = self.nit_tax(conversion_amount2)
        longterm_tax = self.longterm_tax(conversion_amount2)

        return TaxBracket(
            lower=conversion_amount,
            upper=conversion_amount2,
            state=TaxBundle(state_rate, state_marginal, state_tax),
            federal=TaxBundle(federal_rate, federal_marginal, federal_tax),
            nit=TaxBundle(nit_rate, nit_marginal, nit_tax),
            longterm=TaxBundle(longterm_rate, longterm_marginal, longterm_tax)
        )

    def apply_income_tax(self, income, brackets):
        cum_tax = 0.0
        prev_bound = 0
        for rate, bound in brackets:
            if income <= prev_bound:
                break
            cum_tax += (min(bound, income) - prev_bound) * rate
            prev_bound = bound
        return cum_tax

    def apply_capital_tax(self, capital_income, bracket_income, brackets):
        prev_bound = 0
        prev_rate = 0
        for rate, bound in brackets:
            if prev_bound <= bracket_income < bound:
                return rate * capital_income
            prev_bound = bound
            prev_rate = 0
        raise Exception("Should be in a bracket")

    def ordinary_income(self):
        return self.pretax_wage_income + self.ordinary_capital_income - self.federal_deduction

    def state_income(self):
        return self.pretax_wage_income + self.ordinary_capital_income + self.qualified_capital_income - self.state_deduction

    def state_tax(self, conversion_amount):
        adjusted_state_income = self.state_income() + conversion_amount
        return self.apply_income_tax(adjusted_state_income, self.state_brackets)

    def federal_tax(self, conversion_amount):
        adjusted_federal_income = self.ordinary_income() + conversion_amount
        return self.apply_income_tax(adjusted_federal_income, self.federal_brackets)

    def nit_tax(self, conversion_amount):
        adjusted_federal_income = self._income_for_capital_brackets() + conversion_amount
        return self.apply_capital_tax(self.ordinary_capital_income + self.qualified_capital_income, adjusted_federal_income, self.nit_brackets)

    def longterm_tax(self, conversion_amount):
        adjusted_federal_income = self._income_for_capital_brackets() + conversion_amount
        return self.apply_capital_tax(self.qualified_capital_income, adjusted_federal_income, self.longterm_brackets)

    def _income_for_capital_brackets(self):
        return self.ordinary_income() + self.qualified_capital_income

    def _keypoints(self, income, brackets, max_conversion_amount):
        keyponints = []
        for rate, bound in brackets:
            if income > bound:
                continue
            elif income + max_conversion_amount > bound:
                keyponints.append(bound - income)
            else:
                break

        return keyponints

    # return absolute rate and marginal rate
    def rate_at(self, absolute_income, brackets, is_capital=False):
        prev_rate = 0
        prev_bound = 0
        for rate, bound in brackets:
            if absolute_income < bound:
                if not is_capital:
                    return rate, rate
                elif absolute_income == prev_bound:
                    return rate, rate - prev_rate
                else:
                    return rate, 0
            prev_rate = rate
            prev_bound = bound
        return brackets[-1][0], 0

    def _construct_income_keypoints(self, max_conversion_amount):
        keypoints = set([0])
        keypoints.update(self._keypoints(self.ordinary_income(), self.federal_brackets, max_conversion_amount))
        keypoints.update(self._keypoints(self.state_income(), self.state_brackets, max_conversion_amount))
        keypoints.add(max_conversion_amount)
        return sorted(list(keypoints))

    def _construct_capital_keypoints(self, max_conversion_amount):
        keypoints = set()
        keypoints.update(self._keypoints(self._income_for_capital_brackets(), self.nit_brackets, max_conversion_amount))
        keypoints.update(self._keypoints(self._income_for_capital_brackets(), self.longterm_brackets, max_conversion_amount))
        print(keypoints)
        return sorted(list(keypoints))

    def tax_curve(self, max_conversion_amount):
        income_keypoints = self._construct_income_keypoints(max_conversion_amount)
        capital_keypoints = self._construct_capital_keypoints(max_conversion_amount)

        capital_taxes = []
        for conversion_amount in capital_keypoints:
            capital_taxes.append(self._construct_bracket_from_one_point(conversion_amount))

        income_only_curve = []
        for i in range(len(income_keypoints) - 1):
            income_only_curve.append(self._construct_bracket_from_two_points(income_keypoints[i], income_keypoints[i + 1]))

        all_keypoints = sorted(list(set(income_keypoints + capital_keypoints)))
        entire_curve = []
        for i in range(len(all_keypoints) - 1):
            entire_curve.append(self._construct_bracket_from_two_points(all_keypoints[i], all_keypoints[i + 1]))
        return income_only_curve, capital_taxes, entire_curve

    def save_curve(self, max_conversion_amount):
        income_only_curve, capital_taxes, entire_curve = self.tax_curve(max_conversion_amount)
        self.income_only_curve = income_only_curve
        self.capital_taxes = capital_taxes
        self.entire_curve = entire_curve
        self.max_conversion_amount = max_conversion_amount
