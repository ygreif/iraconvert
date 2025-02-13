from os import waitstatus_to_exitcode
from dataclasses import dataclass

MAX_INCOME = 9999999

FEDERAL_2024_SINGLE_BRACKETS = [(.1, 11600), (.12, 47150), (.22, 100525), (.24, 191950), (.32, 243725), (.35, 609351), (.37, MAX_INCOME)]
FEDERAL_2024_MARRIED_BRACKETS = [(.1, 23200), (.12, 94300), (.22, 201050), (.24, 383900), (.32, 487450), (.35, 731200), (.37, MAX_INCOME)]
FEDERAL_2024_HEAD_BRACKETS = [(.1, 16550), (.12, 63100), (.22, 100500), (.24, 191950), (.32, 243700), (.35, 609350), (.37, MAX_INCOME)]

FEDERAL_2025_SINGLE_BRACKETS = [(.1, 11925), (.12, 48475), (.22, 103350), (.24, 197300), (.32, 250525), (.35, 626350), (.37, MAX_INCOME)]
FEDERAL_2025_MARRIED_BRACKETS = [(.1, 23850), (.12, 96950), (.22, 206700), (.24, 394600), (.32, 501050), (.35, 751600), (.37, MAX_INCOME)]
FEDERAL_2025_HEAD_BRACKETS = [(.1, 17000), (.12, 64850), (.22, 103350), (.24, 197300), (.32, 250500), (.35, 626350), (.37, MAX_INCOME)]

CALIFORNIA_2024_SINGLE_BRACKETS = [ (.01, 10756), (.02, 25499), (.04, 40245), (.06, 55866), (.08, 70606), (.093, 360659), (.103, 432787), (.113, 721314), (.123, MAX_INCOME) ]
CALIFORNIA_2024_MARRIED_BRACKETS = [ (.01, 21512), (.02, 50998), (.04, 80490), (.06, 111732), (.08, 141212), (.093, 721318), (.103, 865574), (.113, 1442628), (.123, MAX_INCOME) ]
CALIFORNIA_2024_HEAD_BRACKETS = [ (.01, 21527), (.02, 51000), (.04, 65744), (.06, 81364), (.08, 96107), (.093, 490493), (.103, 588593), (.113, 980987), (.123, MAX_INCOME) ]


def adjust(brackets, ccpi=.03):
    return [(rate, bracket * (1.0 + ccpi)) for rate, bracket in brackets]


FEDERAL_BRACKETS = {
    2024: {
        "single": FEDERAL_2024_SINGLE_BRACKETS,
        "married": FEDERAL_2024_MARRIED_BRACKETS,
        "head": FEDERAL_2024_HEAD_BRACKETS
    },
    2025: {
        "single": FEDERAL_2025_SINGLE_BRACKETS,
        "married": FEDERAL_2025_MARRIED_BRACKETS,
        "head": FEDERAL_2025_HEAD_BRACKETS
    }
}

STATE_BRACKETS = {
    "CA": {
        2024: {
            "single": CALIFORNIA_2024_SINGLE_BRACKETS,
            "married": CALIFORNIA_2024_MARRIED_BRACKETS,
            "head": CALIFORNIA_2024_HEAD_BRACKETS
        },
        2025: {
            "single": adjust(CALIFORNIA_2024_SINGLE_BRACKETS),
            "married": adjust(CALIFORNIA_2024_MARRIED_BRACKETS),
            "head": adjust(CALIFORNIA_2024_HEAD_BRACKETS)
        }
    }
}

STANDARD_DEDUCTIONS = {
    2024: {
        "single": 14600,
        "married": 29200,
        "head": 21900
    },
    2025: {
        "single": 15000,
        "married": 30000,
        "head": 22500
    }
}

GAINS_RATE = {
    2024: {
        "single": [ (0, 47025) ,  (.15, 518900), ( .2, MAX_INCOME) ],
        "married": [ (0, 94050) ,  (.15, 583750), ( .2, MAX_INCOME) ],
        "head": [ (0, 63000) ,  (.15, 551350), ( .2, MAX_INCOME) ]
    },
    2025: {
        "single": [ (0, 48350) ,  (.15, 533400), ( .2, MAX_INCOME) ],
        "married": [ (0, 96700) ,  (.15, 600050), ( .2, MAX_INCOME) ],
        "head": [ (0, 64750) ,  (.15, 566700), ( .2, MAX_INCOME) ]
    }
}

NII_BRACKETS = {
    "single": [ (0, 125000), (.038, MAX_INCOME) ],
    "married": [ (0, 250000), (.038, MAX_INCOME) ],
    "head": [ (0, 200000), (.038, MAX_INCOME) ]
}

def _initial_rates(base_income, brackets):
    for rate, bracket in brackets:
        if base_income < bracket:
            return rate, bracket

def _combine_state_federal_brackets(federal, state):
    federal_idx = 0
    state_idx = 0
    combined = []
    while federal_idx < len(federal) and state_idx < len(state):
        federal_rate, federal_bracket = federal[federal_idx]
        state_rate, state_bracket = state[state_idx]
        if federal_bracket < state_bracket:
            combined.append( (federal_rate + state_rate, federal_bracket)  )
            federal_idx += 1
        else:
            combined.append( (federal_rate + state_rate, state_bracket)  )
            state_idx += 1
    return combined

def _apply_capital_taxes(combined_brackets, capital_brackets, nii_brackets):
    adjusted_brackets = []
    for combined in combined_brackets:
        for capital_rate, capital_bracket in capital_brackets:
            for nii_rate, nii_bracket in nii_brackets:
                lower = max(combined.lower, capital_bracket, nii_bracket)
                upper = min(combined.upper, capital_bracket, nii_bracket)
                if lower < upper:
                    adjusted_brackets.append(CombinedTaxBracket(
                        lower=lower,
                        upper=upper,
                        income_rate=combined.income_rate,
                        marginal_capital=capital_rate,
                        marginal_nii=nii_rate
                    ))
    return adjusted_brackets

def _rates(base_income, max_convert, brackets):
    combined_brackets = []
    max_income = base_income + max_convert
    prev_bracket = 0
    for rate, bracket in brackets:
        if base_income > bracket:
            continue
        elif base_income > prev_bracket:
            upper = min(bracket, base_income + max_convert)
            combined_brackets.append(CombinedTaxBracket(lower=base_income, upper=upper, income_rate=rate, marginal_capital=0, marginal_nii=0))
        elif max_income > prev_bracket:
            upper = min(bracket, base_income + max_convert)
            combined_brackets.append(CombinedTaxBracket(lower=prev_bracket, upper=upper, income_rate=rate, marginal_capital=0, marginal_nii=0))
        else:
            break
        prev_bracket = bracket
    return combined_brackets


def keypoints(base_income, capital_gains, longterm_gains, max_convert, federal_brackets, state_brackets, capital_brackets, nii_brackets):
    brackets = _combine_state_federal_brackets(federal_brackets, state_brackets)
    rates = _rates(base_income, max_convert, brackets)

    return rates


def deduction(status, year):
    return STANDARD_DEDUCTIONS[year][status]
