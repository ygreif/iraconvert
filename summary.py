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

Row = namedtuple('Row', ['Total_Income', 'Conversion_Amount', 'Federal_Tax', 'State_Tax', 'NIT_Tax', 'Longterm_Tax', 'Total_Tax'])

DOLLAR_COLUMNS = ['Total Income', 'Conversion Amount', 'Federal Tax', 'State Tax', 'NIT Tax', 'Longterm Tax', 'Total Tax', 'Total Income Tax', 'Total Capital Taxes', 'IRA Conversion Liability']

def tax_bracket_to_row(bracket, ordinary_income):
    row = Row(
        ordinary_income + bracket.upper,
        bracket.upper,
        bracket.federal.amount,
        bracket.state.amount,
        bracket.nit.amount,
        bracket.longterm.amount,
        bracket.total_tax()
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
    df.columns = ['Total Income', 'Conversion Amount', 'Federal Tax', 'State Tax', 'NIT Tax', 'Longterm Tax', 'Total Tax']
    # transform df to only have Total Income, Conversion Amount, Income Tax, Capital Taxes, Total Tax
    df['Total Income Tax'] = df['Federal Tax'] + df['State Tax']
    df['Total Capital Taxes'] = df['Longterm Tax'] + + df['NIT Tax']
    df['IRA Conversion Liability'] = df['Total Tax'].apply(lambda x: x - total_tax_no_conversion)
    # format the numbers to be dollarized, pass in as a string
    for col in df.columns:
        df[col] = df[col].apply(dollarize_raw_str)

    return df

def table(keypoints: List[float],
          current_income: float,
          longterm_gains: float,
          investment_income: float,
          raw_tax_brackets):
    assert keypoints[0] == current_income
    rows = []
    for total_income in keypoints:
        federal_tax, state_tax, nit_tax, longterm_tax = compute_taxes(total_income, longterm_gains, investment_income, raw_tax_brackets['federal'], raw_tax_brackets['state'], raw_tax_brackets['longterm'], raw_tax_brackets['nit'])
        rows.append(Row(total_income, total_income - current_income, federal_tax, state_tax, nit_tax, longterm_tax, federal_tax + state_tax + nit_tax + longterm_tax))
    total_tax_no_conversion = rows[0].Total_Tax

    df = pd.DataFrame(rows)
    # fix column names
    df.columns = ['Total Income', 'Conversion Amount', 'Federal Tax', 'State Tax', 'NIT Tax', 'Longterm Tax', 'Total Tax']
    # transform df to only have Total Income, Conversion Amount, Income Tax, Capital Taxes, Total Tax
    df['Total Income Tax'] = df['Federal Tax'] + df['State Tax']
    df['Total Capital Taxes'] = df['Longterm Tax'] + + df['NIT Tax']
    df['IRA Conversion Liability'] = df['Total Tax'].apply(lambda x: x - total_tax_no_conversion)
    # format the numbers to be dollarized, pass in as a string
    for col in df.columns:
        df[col] = df[col].apply(dollarize_raw_str)

    return df
