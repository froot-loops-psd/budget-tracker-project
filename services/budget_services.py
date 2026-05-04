import streamlit as st


@st.cache_data(ttl=60, show_spinner=False)
def get_budget(_budget_ws, username: str, month: str):
    """Cached — refreshes every 60 seconds."""
    records = _budget_ws.get_all_records()
    for r in records:
        if r.get("Username") == username and r.get("Month") == month:
            try:
                return float(r["Budget"])
            except (ValueError, TypeError):
                return None
    return None


def set_budget(budget_ws, username: str, month: str, amount: float):
    budget_ws.append_row([username, month, amount], value_input_option="USER_ENTERED")
    get_budget.clear()


def update_budget(budget_ws, username: str, month: str, amount: float):
    rows = budget_ws.get_all_values()
    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 2 and row[0] == username and row[1] == month:
            budget_ws.update_cell(i, 3, amount)
            get_budget.clear()
            return
