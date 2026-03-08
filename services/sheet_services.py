from utils import connect_gsheet


def get_sheet():
    return connect_gsheet()


def ensure_sheet(sh, title: str, headers: list):
    """Return worksheet, creating it with headers if it doesn't exist."""
    try:
        ws = sh.worksheet(title)
        existing = ws.row_values(1)
        if not existing:
            ws.append_row(headers)
        elif existing != headers:
            ws.update(f"A1:{chr(64 + len(headers))}1", [headers])
        return ws
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=1000, cols=max(10, len(headers)))
        ws.append_row(headers)
        return ws


# Re-export for convenience
import gspread  # noqa: E402 — needed for exception reference above
