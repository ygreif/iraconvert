from typing import List
from collections import namedtuple

import pandas as pd
from pandas.core.tools.datetimes import _assemble_from_unit_mappings

from compute_taxes import TaxBracket, compute_taxes
from shared import dollarize_raw, dollarize_raw_str

def explain(schedule_,
            max_conversion,
            future_rate):
    tax_brackets = schedule_.income_only_curve
    first_bracket = tax_brackets[0]

    if max_conversion <= 0:
        return "You have no money to convert. Easy decision."
    elif future_rate < .15:
        return "Your predicted future rate seems unrealistically low. Are you sure you're not missing anything?"
    elif first_bracket.total_income_tax() > future_rate:
        if first_bracket.total_income_tax() < future_rate + .01:
            return "Your current tax rate is slightly higher than your future tax rate. You might consider converting, but it's not a clear win."
        else:
            return "Your current tax rate is higher than your future tax rate. It might not be worth converting."
    for idx in range(len(tax_brackets) - 1):
        bracket = tax_brackets[idx]
        next_bracket = tax_brackets[idx + 1]
        if bracket.total_income_tax() <= future_rate <= next_bracket.total_income_tax():
            max_to_convert = dollarize_raw(str(bracket.upper))
            return f"""Consider converting {dollarize_raw(max_to_convert)} dollars
That will keep your marginal rate at {100 * bracket.total_income_tax():.2f}% which is lower than your expected future tax rate
"""
    return f"""You should convert all of your money. Your current tax rate is lower than your expected future tax rate even if you convert everything.
"""

Row = namedtuple('Row', ['Total_Income', 'Conversion_Amount', 'Federal_Tax', 'State_Tax', 'NIT_Tax', 'Longterm_Tax', 'Total_Tax', 'Marginal_Tax_Rate', 'Capital_Gains_Rate', 'NIT_Rate'])

DOLLAR_COLUMNS = ['Total Income', 'Conversion Amount', 'Federal Tax', 'State Tax', 'NIT Tax', 'Longterm Tax', 'Total Tax', 'Total Income Tax', 'Additional Tax']
PERCENT_COLUMNS = ['Marginal Tax Rate', 'Capital Gains Rate', 'Net Investment Tax Rate']

def tax_bracket_to_row(bracket, ordinary_income):
    row = Row(
        ordinary_income + bracket.upper,
        bracket.upper,
        bracket.federal.amount,
        bracket.state.amount,
        bracket.nit.amount,
        bracket.longterm.amount,
        bracket.total_tax(),
        bracket.total_income_tax(),
        bracket.longterm.rate,
        bracket.nit.rate
    )
    return row

def table2(entire_curve, ordinary_income, initial_tax):
    rows = []
    rows.append(tax_bracket_to_row(initial_tax, ordinary_income))
    for bracket in entire_curve:
        rows.append(tax_bracket_to_row(bracket, ordinary_income))

    df = pd.DataFrame(rows)
    total_tax_no_conversion = rows[0].Total_Tax

    df = pd.DataFrame(rows)
    # fix column names
    df.columns = ['Total Income', 'Conversion Amount', 'Federal Tax', 'State Tax', 'NIT Tax', 'Longterm Tax', 'Total Tax', 'Marginal Tax Rate', 'Capital Gains Rate', 'Net Investment Tax Rate']
    # transform df to only have Total Income, Conversion Amount, Income Tax, Capital Taxes, Total Tax
    df['Total Income Tax'] = df['Federal Tax'] + df['State Tax']
    df['Total Capital Taxes'] = df['Longterm Tax'] +  df['NIT Tax']
    df['Additional Tax'] = df['Total Tax'].apply(lambda x: x - total_tax_no_conversion)
    # format the numbers to be dollarized, pass in as a string
    for col in DOLLAR_COLUMNS:
        df[col] = df[col].apply(dollarize_raw_str)

    for col in PERCENT_COLUMNS:
        df[col] = df[col].apply(lambda x: f"{100 * x:.2f}%")

    return df
