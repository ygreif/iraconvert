from dataclasses import dataclass
from collections import namedtuple

@dataclass
class TaxBracket:
    lower: float
    upper: float
    state_rate: float
    federal_rate: float
    nit: float
    longterm: float

    def total_income_tax(self):
        return self.federal_rate + self.state_rate

def has_next(indices, brackets):
    for key in indices:
        if indices[key] < len(brackets[key]):
            return True
    return False

def min_key(indices, brackets):
    min_key = None
    min_value = float('inf')
    for key in indices:
        index_key = indices[key]
        lst = brackets[key]
        if index_key < len(lst):
            value = lst[index_key][1]
            if value < min_value:
                min_key = key
                min_value = value
    return min_key, brackets[min_key][indices[min_key]]

def rates(base_income, max_convert, federal_brackets, state_brackets, longterm_brackets, nii_brackets, bracket_mode='combine', capital_mode='marginal'):
    indices = {'state': 0, 'federal': 0, 'nit': 0, 'longterm': 0}
    brackets = {'state': state_brackets, 'federal': federal_brackets, 'nit': nii_brackets, 'longterm': longterm_brackets}
    combined = []
    prev_bracket = 0
    while has_next(indices, brackets):
        key, (rate, bracket) = min_key(indices, brackets)
        print("key", key, "rate", rate, "bracket", bracket, "prev_bracket", prev_bracket, indices)
        if base_income > bracket:
            pass
        elif prev_bracket > base_income + max_convert:
            break
        else:
            state_rate = state_brackets[indices['state']][0]
            federal_rate = federal_brackets[indices['federal']][0]
            lower = max(base_income, prev_bracket)
            upper = min(base_income + max_convert, bracket)
            if upper > lower:
                combined.append(TaxBracket(lower=lower, upper=upper, state_rate=state_rate, federal_rate=federal_rate, nit=0, longterm=0))
            if base_income + max_convert > bracket and key == 'nit':
                current_nii_rate = nii_brackets[indices['nit']][0]
                next_nii_rate = nii_brackets[indices['nit'] + 1][0]
                marginal = next_nii_rate - current_nii_rate
                combined.append(TaxBracket(lower=bracket, upper=bracket, state_rate=state_rate, federal_rate=federal_rate, nit=marginal, longterm=0))
            elif base_income + max_convert > bracket and key == 'longterm':
                current_longterm_rate = longterm_brackets[indices['longterm']][0]
                next_longterm_rate = longterm_brackets[indices['longterm'] + 1][0]
                marginal = next_longterm_rate - current_longterm_rate
                combined.append(TaxBracket(lower=bracket, upper=bracket, state_rate=state_rate, federal_rate=federal_rate, nit=0, longterm=marginal))
        indices[key] += 1
        prev_bracket = bracket
    if not bracket_mode == 'split':
        income_brackets = []
        capital_brackets = []
        for bracket in combined:
            if bracket.nit > 0 or bracket.longterm > 0:
                capital_brackets.append(bracket)
            else:
                prev = False if len(income_brackets) == 0 else income_brackets[-1]
                if not prev or not (prev.state_rate == bracket.state_rate and prev.federal_rate == bracket.federal_rate):
                    income_brackets.append(bracket)
                else:
                    prev.upper = bracket.upper
        combined = income_brackets + capital_brackets
    return combined
