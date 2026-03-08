from utils import hash_password


def get_user_row(user_ws, username: str):
    """Return (row_index, hashed_pw) for username, or (None, None)."""
    usernames = user_ws.col_values(1)
    passwords = user_ws.col_values(2)
    if username in usernames:
        idx = usernames.index(username)
        return idx + 1, passwords[idx]   # 1-based row number
    return None, None


def verify_login(user_ws, username: str, password: str) -> bool:
    row_num, stored_hash = get_user_row(user_ws, username)
    if row_num is None:
        return False
    return hash_password(password) == stored_hash


def register_user(user_ws, username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    usernames = user_ws.col_values(1)
    if username in usernames:
        return False, "Username already taken."
    user_ws.append_row([username, hash_password(password)])
    return True, "Account created successfully!"


def reset_password(user_ws, username: str, new_password: str) -> tuple[bool, str]:
    row_num, _ = get_user_row(user_ws, username)
    if row_num is None:
        return False, "Username not found."
    user_ws.update_cell(row_num, 2, hash_password(new_password))
    return True, "Password updated successfully!"
