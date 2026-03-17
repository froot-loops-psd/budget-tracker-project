import pandas as pd


def get_investments(investing_ws, username: str) -> pd.DataFrame:
    records = investing_ws.get_all_records()
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
    investing_ws.append_row([username, date_str, month_str, ticker, amount, return_val])


def delete_investment(investing_ws, username: str, row_index: int):
    """Delete a specific row by its 1-based sheet row index."""
    investing_ws.delete_rows(row_index)
