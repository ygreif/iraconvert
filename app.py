from shiny import App, render, ui, reactive
from shinywidgets import render_plotly, output_widget

import taxes
import graph
import summary

from shared import dollarize, remove_dollar_formatting, clean_df

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.tags.script("""
    function debounce(func, wait) {
        let timeout;
        return function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(), wait);
        };
    }

    const updateWidth = debounce(function() {
        Shiny.setInputValue('window_width', window.innerWidth);
    }, 250);  // Only update after 250ms of no resizing

    document.addEventListener('DOMContentLoaded', updateWidth);
    window.addEventListener('resize', updateWidth);
        """),
        ui.input_text("assets", label="IRA/401k Assets", value="$750,000"),
        ui.input_text("pretax_income", label="Taxable Income", value="$100,000",
                      title="Your total taxable income for the year, including wages, salaries, and other sources"),
        ui.input_text("capital_income", label="Capital Income", value="$40,000",
                      title="Income from investments, such as dividends and short-term capital gains"),
        ui.input_text("longterm_gains", label="Longterm Capital Gains", value="$20,000",
                      title="Profits from selling assets held for more than a year, typically taxed at a lower rate"),
        ui.input_select("tax_year", "Tax Year", {"2024": 2024, "2025": 2025}),
        ui.input_radio_buttons(
            "filing_status",
            "Filing Status",
            {
                'married': "Married filing jointly",
                'single': "Single or filing separately",
                'head': "Head of household"
            }
        ),
        ui.input_checkbox("custom_deduction", "Custom deduction", value=False),
        ui.panel_conditional(
            "input.custom_deduction",
            ui.input_text("deduction", label="Deduction", value="$32,000")
        ),
        ui.panel_conditional(
            "0",
            ui.input_radio_buttons(
                "federal_bracket_type",
                "Federal tax brackets",
                {
                    "default": "Current Tax Brackets",
                },
            )
        ),
        ui.panel_conditional(
            "input.federal_bracket_type === 'custom'",
            ui.markdown("Enter custom federal brackets in the bottom panel"),

        ),
        ui.input_select(
            "state_tax_bracket",
            "State tax brackets",
            {"CA": "California", "none": "No state tax"},
        ),
        ui.panel_conditional(
            "input.state_tax_bracket === 'Custom'",
            ui.markdown("Enter custom state brackets in the bottom panel"),
        ),
        ui.input_numeric("future_tax_rate", "Expected future tax rate", 25, min=0, max=100),
    ),
    ui.layout_columns(
        output_widget("taxburden", height='500px'),
        ui.card(
            ui.card_header("Analysis/Recommendation"),
            ui.output_text("text")
        ),
        ui.output_data_frame("table"),
        col_widths={'md':(12, 3, 9), 'sm':(12, 12, 12) }
    ),
    title="After Tax Calculator",
)

DOLLARIZE_TERMS = ["pretax_income", "capital_income", "longterm_gains", "deduction", "assets"]


    #session.send_input_message(term, numer)


def server(input, output, session):
    @reactive.effect
    def format_inputs():

        for term in DOLLARIZE_TERMS:
            dollarized_income = dollarize(input, term)
            session.send_input_message(term, {"value": dollarized_income})

    @reactive.calc
    def size():
        #import pdb; pdb.set_trace();
        # correspond to sm ec
        width = float(input.window_width())
        if width < 768:
            return 'xs'
        elif width < 992:
            return 'sm'
        elif width < 1200:
            return 'md'
        elif width < 1600:
            return 'lg'
        else:
            return 'xl'

    @reactive.calc
    def width():
        return float(input.window_width())

    @reactive.calc
    def compute():
        amounts = {term: remove_dollar_formatting(input[term]()) for term in DOLLARIZE_TERMS}
        filing_status = input.filing_status()
        tax_year = int(input.tax_year())
        if not input.custom_deduction():
            amounts['deduction'] = taxes.deduction(filing_status, tax_year)

        state = input.state_tax_bracket()

        income = amounts['pretax_income'] - amounts['deduction']
        tax_brackets = taxes.tax_brackets(income, amounts['assets'], amounts['longterm_gains'], amounts['capital_income'], tax_year, filing_status, state)
        future_rate = input.future_tax_rate() / 100
        return income, amounts, tax_brackets, future_rate

    @render.text
    def text():
        income, amounts, tax_brackets, future_rate = compute()
        return summary.explain(income, amounts['longterm_gains'], amounts['capital_income'], tax_brackets, amounts['assets'], future_rate)

    @render.data_frame
    def table():
        income, amounts, tax_brackets, future_rate = compute()
        keypoints = [income] + [b.upper for b in tax_brackets]
        keypoints.sort()

        raw_brackets = taxes.raw_tax_brackets(int(input.tax_year()), input.filing_status(), input.state_tax_bracket())
        df = summary.table(keypoints, income, amounts['longterm_gains'], amounts['capital_income'], raw_brackets)

        df = df[["Conversion Amount", "Total Income Tax", "Total Capital Taxes", "Total Tax"]]

        return df

    @render_plotly
    def taxburden():
        income, amounts, tax_brackets, future_rate = compute()

        plot = graph.plot_tax_brackets(income, amounts['longterm_gains'], amounts['capital_income'], tax_brackets, future_rate, amounts['assets'])

        if size() in ('xs', 'sm'):
            plot.update_layout(showlegend=False)
        # elapsed time
        return plot  #.update_layout(autosize=True, height=Noneb, width=None).update_traces(marker=dict(size=10))  # Ensure it adapts dynamically


app = App(app_ui, server)
