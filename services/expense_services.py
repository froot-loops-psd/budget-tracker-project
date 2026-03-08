import pandas as pd


def get_user_expenses(expense_ws, username: str) -> pd.DataFrame:
    records = expense_ws.get_all_records()
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame()
    df = df[df["Username"] == username].copy()
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def add_expense(
    expense_ws,
    username: str,
    description: str,
    amount: float,
    category: str,
    date_str: str,
    month_str: str,
):
    expense_ws.append_row([username, description, amount, category, date_str, month_str])


def auto_archive(expense_ws, archive_ws, current_month: str):
    """Move all rows not belonging to current_month into archive sheet."""
    all_vals = expense_ws.get_all_values()
    if len(all_vals) <= 1:
        return

    header = all_vals[0]
    try:
        month_col = header.index("Month")
    except ValueError:
        return  # Sheet structure unexpected, skip safely

    keep = [header]
    to_archive = []

    for row in all_vals[1:]:
        row = (row + [""] * len(header))[: len(header)]
        if row[month_col] != current_month:
            to_archive.append(row)
        else:
            keep.append(row)

    if not to_archive:
        return

    # Append old rows to archive
    arch_header = archive_ws.row_values(1)
    if arch_header != header:
        archive_ws.clear()
        archive_ws.append_row(header)
    for row in to_archive:
        archive_ws.append_row(row)

    # Rewrite expense sheet with only current-month rows
    expense_ws.clear()
    for row in keep:
        expense_ws.append_row(row)
