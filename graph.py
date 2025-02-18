from compute_taxes import TaxBracket
from dataclasses import dataclass
import plotly.graph_objects as go
from typing import List

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

    hit_conversion = False
    total_tax = 0
    for bracket in tax_brackets:
        if bracket.nit > 0 or bracket.longterm > 0:
            hit_conversion = True
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

    """
    # plot with seaborn
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x=conversion_amounts, y=taxes, ax=ax)
    ax.set_title('Total Tax vs Roth Conversion Amount')
    ax.set_xlabel('Roth Conversion Amount ($)')
    ax.set_ylabel('Total Tax ($)')
    plt.show()
    """


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
    fig = plot_roth_conversion_tax(10, 50000, 10000, 120000, brackets, 120000)
    fig.show()
