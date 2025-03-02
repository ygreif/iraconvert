from dataclasses import dataclass
import compute_taxes
import simple_taxes

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

NO_INCOME_BRACKET = [(0, MAX_INCOME),]

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

@dataclass
class CombinedTaxBracket:
    lower: float
    upper: float
    income_rate: float
    marginal_capital: float
    marginal_nii: float

def _apply_capital_taxes(base_income, max_convert, income_brackets, capital_brackets, type_):
    prev_rate = capital_brackets[-1][0]
    prev_upper = capital_brackets[-1][1]


def get_federal_brackets(year):
    return FEDERAL_BRACKETS[year]

def get_state_brackets(state, year, status):
    if not state in STATE_BRACKETS:
        return NO_INCOME_BRACKET
    return STATE_BRACKETS[state][year][status]

def get_gains_brackets(year):
    return GAINS_RATE[year]

def get_nii_brackets():
    return NII_BRACKETS

def raw_tax_brackets(year, status, state):
    return {'federal': get_federal_brackets(year)[status], 'state': get_state_brackets(state, year, status), 'longterm': get_gains_brackets(year)[status], 'nit': get_nii_brackets()[status]}

def tax_brackets(base_income, max_convert, longterm_gains, investment_income, year, status, state):
    federal_brackets = get_federal_brackets(year)[status]
    state_brackets = get_state_brackets(state, year, status)
    gains_brackets = get_gains_brackets(year)[status]
    nii_brackets = get_nii_brackets()[status]

    return compute_taxes.rates(base_income, max_convert, federal_brackets, state_brackets, gains_brackets, nii_brackets)

def deduction(status, year):
    return STANDARD_DEDUCTIONS[year][status]

def state_deduction(status, year, state):
    if not state in STATE_DEDUCTIONS:
        return 0
    return STATE_DEDUCTIONS[state][year][status]

def schedule(base_income, max_convert, longterm_gains, investment_income, year, status, state, custom_deduction=None):
    federal_brackets = get_federal_brackets(year)[status]
    state_brackets = get_state_brackets(state, year, status)
    gains_brackets = get_gains_brackets(year)[status]
    nii_brackets = get_nii_brackets()[status]

    federal_deduction = custom_deduction if custom_deduction is not None else deduction(status, year)
    state_deduction = 0
    schedule = simple_taxes.TaxSchedule(
        base_income, investment_income, longterm_gains, federal_brackets, state_brackets, nii_brackets, gains_brackets, federal_deduction, state_deduction)
    schedule.save_curve(max_convert)
    return schedule

STATE_DEDUCTIONS = {
    "CA": {
        2024: {
            "single": 5540,
            "married": 11080,
            "head": 11080
        }
    }
}
