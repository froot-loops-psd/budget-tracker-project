DEFAULT_CATEGORIES = [
    "Coffee", "Cig", "Expense", "FnB",
    "Investing", "Liability", "Other",
    "Saving", "Transport",
]


def get_user_categories(cat_ws, username: str) -> list[str]:
    """Merge default + user-custom categories, sorted."""
    records = cat_ws.get_all_records()
    custom = [
        r["CategoryName"]
        for r in records
        if r.get("Username") == username and r.get("CategoryName")
    ]
    return sorted(set(DEFAULT_CATEGORIES + custom))


def add_category(cat_ws, username: str, category_name: str):
    cat_ws.append_row([username, category_name])


def delete_category(cat_ws, username: str, category_name: str) -> bool:
    """Delete a custom category row. Returns True if something was deleted."""
    rows = cat_ws.get_all_values()
    if not rows:
        return False
    header = rows[0]
    kept = [header]
    deleted = False
    for row in rows[1:]:
        row = (row + [""] * len(header))[: len(header)]
        if row[0] == username and row[1] == category_name:
            deleted = True
        else:
            kept.append(row)
    if deleted:
        cat_ws.clear()
        for r in kept:
            cat_ws.append_row(r)
    return deleted
