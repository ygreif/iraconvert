from typing import List
from collections import namedtuple

import pandas as pd

from compute_taxes import TaxBracket, compute_taxes
from shared import dollarize_raw, dollarize_raw_str

def explain(current_income: float,
            longterm_gains: float,
            investment_income: float,
            tax_brackets: List[TaxBracket],
            max_conversion: float,
            future_rate):
    if max_conversion <= 0:
        return "You have no money to convert. Easy decision."
    elif future_rate < .15:
        return "Your predicted future rate seems unrealistically low. Are you sure you're not missing anything?"
    elif tax_brackets[0].total_income_tax() > future_rate:
        if tax_brackets[0].total_income_tax() > future_rate + .01:
            return "Your current tax rate is slightly higher than your future tax rate. You might consider converting, but it's not a clear win."
        else:
            return "Your current tax rate is higher than your future tax rate. It might not be worth converting."
    for idx in range(len(tax_brackets) - 1):
        bracket = tax_brackets[idx]
        next_bracket = tax_brackets[idx + 1]
        if bracket.total_income_tax() <= future_rate <= next_bracket.total_income_tax():
            max_to_convert = dollarize_raw(str(bracket.upper - current_income))
            return f"""Consider converting {dollarize_raw(max_to_convert)} dollars
That will keep your marginal rate at {100 * bracket.total_income_tax():.2f}% which is lower than your expected future tax rate
"""
        else:
            return f"""You should convert all of your money. Your current tax rate is lower than your expected future tax rate even if you convert everything.
"""

Row = namedtuple('Row', ['Total_Income', 'Conversion_Amount', 'Federal_Tax', 'State_Tax', 'NIT_Tax', 'Longterm_Tax', 'Total_Tax'])

def table(keypoints: List[float],
          current_income: float,
          longterm_gains: float,
          investment_income: float,
          raw_tax_brackets):
    rows = []
    for total_income in keypoints:
        federal_tax, state_tax, nit_tax, longterm_tax = compute_taxes(total_income, longterm_gains, investment_income, raw_tax_brackets['federal'], raw_tax_brackets['state'], raw_tax_brackets['longterm'], raw_tax_brackets['nit'])
        rows.append(Row(total_income, total_income - current_income, federal_tax, state_tax, nit_tax, longterm_tax, federal_tax + state_tax + nit_tax + longterm_tax))
    df = pd.DataFrame(rows)
    # fix column names
    df.columns = ['Total Income', 'Conversion Amount', 'Federal Tax', 'State Tax', 'NIT Tax', 'Longterm Tax', 'Total Tax']
    # transform df to only have Total Income, Conversion Amount, Income Tax, Capital Taxes, Total Tax
    df['Total Income Tax'] = df['Federal Tax'] + df['State Tax'] + df['NIT Tax']
    df['Total Capital Taxes'] = df['Longterm Tax']

#    df = df[['Conversion Amount', 'Total Income Tax', 'Total Capital Taxes', 'Total Tax']]

    # format the numbers to be dollarized, pass in as a string
    for col in df.columns:
        df[col] = df[col].apply(dollarize_raw_str)

    return df
