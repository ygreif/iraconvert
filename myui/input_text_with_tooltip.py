from typing import Literal, Optional
from htmltools import Tag, TagChild, css, div, span
from shiny import ui
#from icons import question_circle_fill
from shiny.ui import input_text

def input_text_with_tooltip(
    id: str,
    label: TagChild,
    tooltip: str,
    value: str = "",
    *,
    width: Optional[str] = None,
    placeholder: Optional[str] = None,
    autocomplete: Optional[str] = "off",
    spellcheck: Optional[Literal["true", "false"]] = None,
) -> Tag:
    """
    Create an input text control with an associated tooltip.

    This function wraps the standard input_text component and adds a tooltip
    capability while maintaining all original functionality.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    tooltip
        Tooltip text to display when hovering over question mark icon.
    value
        Initial value.
    width
        The CSS width, e.g., '400px', or '100%'.
    placeholder
        A hint as to what can be entered into the control.
    autocomplete
        Whether to enable browser autocompletion of the text input.
    spellcheck
        Whether to enable browser spell checking of the text input.

    Returns
    -------
    :
        A UI element with tooltip
    """
    question_mark = span(
        "❓",
        style="""
            display: inline-block;
            cursor: help;
            font-size: 0.9em;
            vertical-align: middle;
        """
    )

    question_mark = span(
        "?",
        style="""
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 1px solid currentColor;
            font-size: 12px;
            line-height: 1;
            cursor: help;
            color: #6c757d;  /* Bootstrap's text-muted color */
            margin-left: 0.5rem;
            opacity: 0.8;
            transition: opacity 0.15s ease-in-out;
        """
    )

    # Create the enhanced label with tooltip
    enhanced_label = div(
        span(label),
        ui.tooltip(
            question_mark,  # trigger element
            tooltip,        # tooltip message
            placement="right"
        ),
        style="display: flex; align-items: center; gap: 0.25rem;"
    )

    # Use the original input_text with our enhanced label
    input_element = input_text(
        id=id,
        label=enhanced_label,  # Pass our enhanced label instead of the original
        value=value,
        width=width,
        placeholder=placeholder,
        autocomplete=autocomplete,
        spellcheck=spellcheck
    )

    return input_element
