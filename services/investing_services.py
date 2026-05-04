import pandas as pd
import streamlit as st


@st.cache_data(ttl=30, show_spinner=False)
def get_investments(_investing_ws, username: str) -> pd.DataFrame:
    records = _investing_ws.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()
    df = df[df["Username"] == username].copy()
    for col in ["Amount", "Return"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def add_investment(
    investing_ws,
    username: str,
    date_str: str,
    month_str: str,
    ticker: str,
    amount: float,
    return_val: float,
):
    investing_ws.append_row(
        [username, date_str, month_str, ticker, amount, return_val],
        value_input_option="USER_ENTERED",
    )
    get_investments.clear()
