import pandas as pd
import streamlit as st


@st.cache_data(ttl=30, show_spinner=False)
def get_savings(_savings_ws, username: str) -> pd.DataFrame:
    records = _savings_ws.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()
    df = df[df["Username"] == username].copy()
    for col in ["Amount", "Goal"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def get_monthly_savings(_savings_ws, username: str, month: str):
    records = _savings_ws.get_all_records()
    for r in records:
        if r.get("Username") == username and r.get("Month") == month:
            return float(r.get("Amount") or 0), float(r.get("Goal") or 0)
    return None, None


def set_savings(savings_ws, username: str, month: str, amount: float, goal: float):
    savings_ws.append_row([username, month, amount, goal], value_input_option="USER_ENTERED")
    get_savings.clear()
    get_monthly_savings.clear()


def update_savings(savings_ws, username: str, month: str, amount: float, goal: float):
    rows = savings_ws.get_all_values()
    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 2 and row[0] == username and row[1] == month:
            savings_ws.update_cell(i, 3, amount)
            savings_ws.update_cell(i, 4, goal)
            get_savings.clear()
            get_monthly_savings.clear()
            return
