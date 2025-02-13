import seaborn as sns
import taxes


# Import data from shared.py
from shared import df

from shiny import App, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
#        ui.input_text("assets", label="IRA/401k Assets", value="$50,000"),
        ui.input_text("pretax_income", label="Taxable Income", value="$100,000"),
        ui.input_select("tax_year", "Tax Year", {"2024": 2024, "2025": 2025}),
        ui.input_radio_buttons(
            "deduction_type",
            "Deduction Type",
            {
                'married': "Married filing jointly",
                'single': "Single or filing separately",
                'zcustom': "Custom",
            }
        ),
        ui.panel_conditional(
            "input.deduction_type === 'zcustom'",
            ui.input_text("deduction", label="Deduction")
        ),
        ui.input_radio_buttons(
            "federal_bracket_type",
            "Federal tax brackets",
            {
                "default": "Current Tax Brackets",
                "wotija": "Brackets if Trump tax cuts expire",
                "custom": "Custom"
            }
        ),
        ui.panel_conditional(
            "input.federal_bracket_type === 'custom'",
            ui.markdown("Enter custom federal brackets in the bottom panel"),

        ),
        ui.input_select(
            "state_tax_bracket",
            "State tax brackets",
            {"Custom": "Custom", "none": "None", "california": "California"},
        ),
        ui.panel_conditional(
            "input.state_tax_bracket === 'Custom'",
            ui.markdown("Enter custom state brackets in the bottom panel"),
        ),
        ui.input_numeric("future_tax_rate", "Expected future tax rate", 25, min=0, max=100),
    ),
    ui.output_plot("hist"),
    title="Hello sidebar!",
)

def dollarize(input, term):
    raw_value = input[term]()
    numeric_value = raw_value
    try:
        numeric_value = float(raw_value.replace("$", "").replace(",", ""))
        if '.' in raw_value:
            numeric_value = f"${numeric_value:,.2f}"
        else:
            numeric_value = f"${numeric_value:,.0f}"
    except ValueError as e:
        print(e)
    return numeric_value


    #session.send_input_message(term, numer)


def server(input, output, session):
    @reactive.effect
    def format_inputs():
        dollarized_income = dollarize(input, "pretax_income")
        print("Sending message", dollarized_income)
        session.send_input_message("pretax_income", {"value": dollarized_income})
        #session.send_input_message("pretax_income", dollarized_income)

    @render.plot
    def taxburden():
        pretax_income = input.pretax_income()
        deduction_type = input.deduction_type()
        if deduction_type == "zcustom":
            deduction = input.deduction()
        else:
            deduction = taxes.deduction(deduction_type, input.tax_year())






app = App(app_ui, server)
