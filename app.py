import seaborn as sns
from shared import df

from shiny import App, render, ui, reactive
from shinywidgets import render_plotly, output_widget

import taxes
import graph

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("assets", label="IRA/401k Assets", value="$750,000"),
        ui.input_text("pretax_income", label="Taxable Income", value="$100,000"),
        ui.input_text("capital_income", label="Capital Income", value="$40,000"),
        ui.input_text("longterm_gains", label="Longterm Capital Gains", value="$20,000"),
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
    output_widget("taxburden"),
    #i.output_text_verbatim("text"),
    title="After Tax Calculator",
)

DOLLARIZE_TERMS = ["pretax_income", "capital_income", "longterm_gains", "deduction", "assets"]

def remove_dollar_formatting(amount):
    return float(amount.replace("$", "").replace(",", ""))

def dollarize(input, term):
    raw_value = input[term]()
    numeric_value = raw_value
    try:
        numeric_value = remove_dollar_formatting(raw_value)
        if '.' in raw_value:
            numeric_value = f"${numeric_value:,.2f}"
        else:
            numeric_value = f"${numeric_value:,.0f}"
    except ValueError as e:
        print(e, term, raw_value)
    return numeric_value


    #session.send_input_message(term, numer)


def server(input, output, session):
    @reactive.effect
    def format_inputs():
        print("Formatting inputs")
        for term in DOLLARIZE_TERMS:
            dollarized_income = dollarize(input, term)
            session.send_input_message(term, {"value": dollarized_income})



    @render_plotly
    def taxburden():
        amounts = {term: remove_dollar_formatting(input[term]()) for term in DOLLARIZE_TERMS}
        filing_status = input.filing_status()
        tax_year = int(input.tax_year())
        if not input.custom_deduction():
            amounts['deduction'] = taxes.deduction(filing_status, tax_year)

        state = input.state_tax_bracket()

        income = amounts['pretax_income'] - amounts['deduction']
        tax_brackets = taxes.tax_brackets(income, amounts['assets'], amounts['longterm_gains'], amounts['capital_income'], tax_year, filing_status, state)
        future_rate = input.future_tax_rate() / 100

        plot = graph.plot_tax_brackets(income, amounts['longterm_gains'], amounts['capital_income'], tax_brackets, future_rate, amounts['assets'])
        print(plot)
        return plot

app = App(app_ui, server)
