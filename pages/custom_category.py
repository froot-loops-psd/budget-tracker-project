import streamlit as st
from utils import connect_gsheet
from services.sheet_services import ensure_sheet
from services.category_services import (
    get_user_categories,
    add_category,
    delete_category,
    DEFAULT_CATEGORIES,
)
from theme import apply_theme, theme_toggle

st.set_page_config(page_title="Categories", page_icon="🏷️", layout="centered")
apply_theme()

# ── GUARD ─────────────────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.warning("🔒 Please login first.")
    st.stop()

USERNAME = st.session_state["username"]

# ── SHEETS ────────────────────────────────────────────────────────────────────
sh          = connect_gsheet()
category_ws = ensure_sheet(sh, "Categories", ["Username", "CategoryName"])

# ── DATA ──────────────────────────────────────────────────────────────────────
all_cats    = get_user_categories(category_ws, USERNAME)
custom_cats = [c for c in all_cats if c not in DEFAULT_CATEGORIES]

# ── UI ────────────────────────────────────────────────────────────────────────
col_back, _, col_toggle = st.columns([1, 3, 1.4])
with col_back:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/tracker.py")
with col_toggle:
    theme_toggle()

st.markdown('<div class="title-gradient" style="font-size:1.6rem;">🏷️ Manage Categories</div>', unsafe_allow_html=True)
st.markdown(f"<div class='subtitle' style='margin-bottom:1.5rem'>Logged in as <b>{USERNAME}</b></div>", unsafe_allow_html=True)

# Default categories (read-only)
st.markdown("**Default categories** — always available, cannot be deleted:")
st.markdown(" ".join(f'<span class="badge">{c}</span>' for c in DEFAULT_CATEGORIES), unsafe_allow_html=True)

st.markdown("<br>**Your custom categories:**", unsafe_allow_html=True)
if custom_cats:
    st.markdown(" ".join(f'<span class="badge badge-custom">{c}</span>' for c in custom_cats), unsafe_allow_html=True)
else:
    st.markdown('<span style="color:var(--muted);font-size:0.85rem">None yet — add one below.</span>', unsafe_allow_html=True)

st.markdown("---")

col_add, col_del = st.columns(2)

# ── ADD ───────────────────────────────────────────────────────────────────────
with col_add:
    st.markdown("#### ➕ Add Category")
    with st.form("add_cat_form", clear_on_submit=True):
        new_cat = st.text_input("Category name")
        if st.form_submit_button("Add", use_container_width=True):
            nc = new_cat.strip()
            if not nc:
                st.error("Name cannot be blank.")
            elif nc in all_cats:
                st.warning(f'"{nc}" already exists.')
            else:
                add_category(category_ws, USERNAME, nc)
                st.success(f'"{nc}" added!')
                st.rerun()

# ── DELETE ────────────────────────────────────────────────────────────────────
with col_del:
    st.markdown("#### 🗑️ Delete Custom Category")
    if not custom_cats:
        st.info("No custom categories to delete.")
    else:
        with st.form("del_cat_form"):
            del_choice = st.selectbox("Choose category to delete", ["-"] + custom_cats)
            if st.form_submit_button("Delete", use_container_width=True):
                if del_choice == "-":
                    st.info("Pick a category first.")
                else:
                    deleted = delete_category(category_ws, USERNAME, del_choice)
                    if deleted:
                        st.success(f'"{del_choice}" deleted.')
                        st.rerun()
                    else:
                        st.error("Something went wrong — category not found.")

st.markdown("---")
st.caption("Custom categories are per-user. Default categories are shared across all users.")
