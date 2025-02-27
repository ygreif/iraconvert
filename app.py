from shiny import App, render, ui, reactive
from shinywidgets import render_plotly, output_widget

import myui.input_text_with_tooltip as uix

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
        uix.input_text_with_tooltip("pretax_income", label="Wage Income", value="$100,000", tooltip="Wage income after adjustments eg 1040 box 1"),
        uix.input_text_with_tooltip("capital_income", label="Ordinary Capital Income", tooltip="Ordinary dividends and short term capital gains", value="$40,000"),
        uix.input_text_with_tooltip("longterm_gains", label="Qualified Capital Gains", value="$20,000", tooltip="Qualified dividends and longterm capital gains"),
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
    def schedule():
        amounts = {term: remove_dollar_formatting(input[term]()) for term in DOLLARIZE_TERMS}
        filing_status = input.filing_status()
        tax_year = int(input.tax_year())
        if not input.custom_deduction():
            amounts['deduction'] = taxes.deduction(filing_status, tax_year)

        state = input.state_tax_bracket()

        return taxes.schedule(amounts['pretax_income'], amounts['assets'], amounts['longterm_gains'], amounts['capital_income'], tax_year, filing_status, state)

    @render.text
    def text():
        future_rate = input.future_tax_rate() / 100
        schedule_ = schedule()
        return summary.explain(schedule_, schedule_.max_conversion_amount, future_rate)

    @render.data_frame
    def table():
        schedule_ = schedule()
        df = summary.table2(schedule_.entire_curve, schedule_.pretax_wage_income, schedule_.initial_tax)

        df = df[["Conversion Amount", "Additional Tax", "Marginal Tax Rate", "Capital Gains Rate", "Net Investment Tax Rate"]]

        return df

    @reactive.calc
    def future_rate():
        future_rate = input.future_tax_rate() / 100
        return future_rate

    @render_plotly
    def taxburden():
        schedule_ = schedule()
        plot = graph.plot_tax_brackets(schedule_.pretax_wage_income, schedule_.qualified_capital_income, schedule_.ordinary_capital_income, schedule_.income_only_curve, schedule_.capital_taxes, future_rate(), schedule_.max_conversion_amount)

        if size() in ('xs', 'sm'):
            plot.update_layout(showlegend=False)
        # elapsed time
        return plot  #.update_layout(autosize=True, height=Noneb, width=None).update_traces(marker=dict(size=10))  # Ensure it adapts dynamically


app = App(app_ui, server)
