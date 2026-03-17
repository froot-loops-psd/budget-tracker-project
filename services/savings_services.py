import pandas as pd


def get_savings(savings_ws, username: str) -> pd.DataFrame:
    records = savings_ws.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()
    df = df[df["Username"] == username].copy()
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    if "Goal" in df.columns:
        df["Goal"] = pd.to_numeric(df["Goal"], errors="coerce").fillna(0.0)
    return df


def get_monthly_savings(savings_ws, username: str, month: str):
    """Return (amount, goal) for a specific month, or (None, None)."""
    records = savings_ws.get_all_records()
    for r in records:
        if r.get("Username") == username and r.get("Month") == month:
            return float(r.get("Amount") or 0), float(r.get("Goal") or 0)
    return None, None


def set_savings(savings_ws, username: str, month: str, amount: float, goal: float):
    savings_ws.append_row([username, month, amount, goal])


def update_savings(savings_ws, username: str, month: str, amount: float, goal: float):
    rows = savings_ws.get_all_values()
    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 2 and row[0] == username and row[1] == month:
            savings_ws.update_cell(i, 3, amount)
            savings_ws.update_cell(i, 4, goal)
            return
