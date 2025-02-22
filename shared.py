import pandas as pd

def dollarize_raw_str(raw_value):
    return dollarize_raw(str(raw_value))

def dollarize_raw(raw_value):
    numeric_value = raw_value
    try:
        numeric_value = remove_dollar_formatting(raw_value)
        if '.' in raw_value:
            numeric_value = f"${numeric_value:,.2f}"
        else:
            numeric_value = f"${numeric_value:,.0f}"
    except ValueError as e:
        print(e, raw_value)
    return numeric_value


def dollarize(input, term):
    raw_value = input[term]()
    return dollarize_raw(raw_value)

def remove_dollar_formatting(amount):
    return float(amount.replace("$", "").replace(",", ""))

def clean_df(df):
    df_dict = df.to_dict(orient='records')
    new_df = pd.DataFrame(df_dict)
    return new_df
