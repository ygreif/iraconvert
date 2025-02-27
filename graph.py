from simple_taxes import TaxBracket
from dataclasses import dataclass
import plotly.graph_objects as go
from typing import List


def plot_tax_brackets(current_income: float,
                      longterm_gains: float,
                      investment_income: float,
                      income_brackets: List[TaxBracket],
                      capital_brackets: List[TaxBracket],
                      future_rate: float,
                      max_conversion: float) -> go.Figure:
    """
    Creates a plot showing marginal tax rates for different Roth conversion amounts.
    Handles regular income tax, long-term capital gains, and investment income tax.
    """
    # Get key points where tax calculation changes
    taxes = []
    conversion_amounts = []
    hovertext = []
    names = []

    total_income = current_income + longterm_gains + investment_income

    for idx in range(len(income_brackets)):
        bracket = income_brackets[idx]
        if bracket.state.rate:
            hovertext.append( [f"Federal rate {100*bracket.federal.rate:.2f}%, state rate {100*bracket.state.rate:.2f}%"] * 2)
            names.append(f"Combined rate {100*(bracket.federal.rate+bracket.state.rate):.2f}%, federal rate {100*bracket.federal.rate:.2f}%, state rate {100*bracket.state.rate:.2f}%")
        else:
            hovertext.append([f"Federal rate {100*bracket.federal.rate:.2f}%"] * 2)
            names.append(f"Federal rate {100*bracket.federal.rate:.2f}%")
        taxes.append([bracket.state.rate + bracket.federal.rate] * 2)
        conversion_amounts.append([bracket.lower - current_income, bracket.upper - current_income])

    for idx in range(len(capital_brackets)):
        bracket = capital_brackets[idx]
        income_rate = bracket.state.rate + bracket.federal.rate
        if bracket.nit.marginal > 0:
            marginal_nit = bracket.nit.marginal #- cur_nit
            nit_rate = ((investment_income + longterm_gains) * marginal_nit) / total_income
            hovertext.append([f"Effective Net Investment Tax rate is {100*nit_rate:.2f}% "])
            taxes.append([nit_rate + income_rate])
            names.append(f"NIT tax of {100 * marginal_nit:.2f}% on capital income")
        elif bracket.longterm.rate > 0:
            marginal_longterm = bracket.longterm.marginal
            capital_rate = (longterm_gains * marginal_longterm) / total_income
            hovertext.append([
                f"Longterm capital gains increased by {100 * marginal_longterm:.2f}% increasing your effective tax rate by {100*capital_rate:.2f}%"])
            names.append(f"Longterm capital gains tax increase of {100* marginal_longterm:.2f}% on capital income")
            taxes.append([capital_rate + income_rate])
        else:
            raise Exception("Bracket labeled capital but no capital gain")
        conversion_amounts.append([bracket.upper - current_income])

    # Create the plot
    fig = go.Figure()
    for amounts, tax, hover, name in zip(conversion_amounts, taxes, hovertext, names):
        if len(amounts) > 1:
             fig.add_trace(go.Scatter(
                x=amounts,
                y=tax,
                hovertext=hover,
                 hovertemplate='%{hovertext}<extra></extra>',
                mode='lines',
                name=name,
                line=dict(width=4)))
        else:
            fig.add_trace(go.Scatter
                          (x=amounts,
                           y=tax,
                           hovertext=hover,
                           hovertemplate='%{hovertext}<extra></extra>',
                           mode='markers',
                            name=name,
                           marker=dict(size=10)))

    # Add future rate line
    fig.add_trace(go.Scatter(
        x=[0, max_conversion],
        y=[future_rate] * 2,
        mode='lines',
        name='Future Rate',
        line=dict(width=4, dash='dash')
    ))

    fig.update_xaxes(tickprefix="$")
    fig.update_yaxes(tickformat=',.0%',)

    fig.update_layout(
        title='Tax Rate vs Roth Conversion Amount',
        xaxis_title='Roth Conversion Amount ($)',
        yaxis_title='Margianl Tax Rate',
        hovermode='closest',
        showlegend=True,
        height=500
    )
    fig.update_layout(legend=dict(
        yanchor="top",
        orientation="h",
        xanchor="left",
        x=0,
        y=-.15
    ))

    return fig



def plot_roth_conversion_tax(current_income: float,
                           longterm_gains: float,
                           investment_income: float,
                           max_amount: float,
                          tax_brackets: List[TaxBracket],
                           max_conversion: float) -> go.Figure:
    """
    Creates a plot showing total tax owed for different Roth conversion amounts.
    Handles regular income tax, long-term capital gains, and investment income tax.
    """
    # Get key points where tax calculation changes
    taxes = [0]
    conversion_amounts = [0]
    names = []
    last_total = None
    discontinuities = []  # Track points where we need to break the line

    hit_capital = False
    total_tax = 0
    for bracket in tax_brackets:
        if bracket.nit > 0 or bracket.longterm > 0:
            hit_capital = True
            if last_total is not None:
                discontinuities.append(len(taxes))
            if bracket.nit > 0:
                total_tax += investment_income * bracket.nit
            if bracket.longterm > 0:
                total_tax += longterm_gains * bracket.longterm
        else:
            taxable_in_bracket = bracket.upper - bracket.lower
            if taxable_in_bracket > 0:
                total_tax += taxable_in_bracket * (bracket.state_rate + bracket.federal_rate)
        taxes.append(total_tax)
        conversion_amounts.append(bracket.upper - current_income)
        last_total = total_tax

    # Create the plot
    fig = go.Figure()

    # Split the line at discontinuities
    start_idx = 0
    for end_idx in discontinuities:
        fig.add_trace(go.Scatter(
            x=conversion_amounts[start_idx:end_idx],
            y=taxes[start_idx:end_idx],
            mode='lines',
            name=f'Tax Segment {start_idx+1}',
            line=dict(width=4),
            showlegend=False
        ))
        start_idx = end_idx

    # Add final segment
    fig.add_trace(go.Scatter(
        x=conversion_amounts[start_idx:],
        y=taxes[start_idx:],
        mode='lines',
        name=f'Tax Segment {len(discontinuities)+1}',
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        title='Total Tax vs Roth Conversion Amount',
        xaxis_title='Roth Conversion Amount ($)',
        yaxis_title='Total Tax ($)',
        hovermode='x',
        showlegend=False
    )

    return fig


if __name__ == '__main__':
    brackets = [
            TaxBracket(lower=50000, upper=50000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=.15),
            TaxBracket(lower=50000, upper=60000, state_rate=0.09, federal_rate=0.12, nit=0, longterm=0),
            TaxBracket(lower=60000, upper=100000, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0),
            TaxBracket(lower=100000, upper=100000, state_rate=0.09, federal_rate=0.22, nit=.038, longterm=0),
            TaxBracket(lower=100000, upper=120010, state_rate=0.09, federal_rate=0.22, nit=0, longterm=0),
        ]
    fig = plot_tax_brackets(50000, 10000, 1000, 100000, brackets, 100000)
    fig.show()
