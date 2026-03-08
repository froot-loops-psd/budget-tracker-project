import streamlit as st
from utils import connect_gsheet
from services.sheet_services import ensure_sheet
from services.category_services import (
    get_user_categories,
    add_category,
    delete_category,
    DEFAULT_CATEGORIES,
)

st.set_page_config(page_title="Categories", page_icon="🏷️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400&display=swap');
html,body,[class*="css"]{background:#0e0f13;color:#e8eaf2;font-family:'DM Mono',monospace;}
header[data-testid="stHeader"],footer,#MainMenu{display:none;}
h1,h2,h3{font-family:'Syne',sans-serif;font-weight:800;}
.stTextInput>div>div>input{background:#1c1f2a!important;border:1px solid #2a2d3a!important;border-radius:10px!important;color:#e8eaf2!important;}
.stButton>button{background:linear-gradient(135deg,#7c6af7,#6254d4)!important;color:white!important;border:none!important;border-radius:10px!important;font-family:'DM Mono',monospace!important;}
.stSelectbox>div>div{background:#1c1f2a!important;border:1px solid #2a2d3a!important;border-radius:10px!important;color:#e8eaf2!important;}
.badge{display:inline-block;background:#1c1f2a;border:1px solid #2a2d3a;border-radius:99px;padding:0.2rem 0.75rem;font-size:0.75rem;color:#7b7f96;margin:0.15rem;}
.badge-custom{border-color:#7c6af7;color:#7c6af7;}
</style>
""", unsafe_allow_html=True)

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
col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Back"):
        st.switch_page("pages/tracker.py")

st.markdown("## 🏷️ Manage Categories")
st.markdown(f"<div style='color:#7b7f96;font-size:0.82rem;margin-bottom:1.5rem'>Logged in as <b>{USERNAME}</b></div>", unsafe_allow_html=True)

# Default categories (read-only)
st.markdown("**Default categories** — always available, cannot be deleted:")
st.markdown(" ".join(f'<span class="badge">{c}</span>' for c in DEFAULT_CATEGORIES), unsafe_allow_html=True)

st.markdown("<br>**Your custom categories:**", unsafe_allow_html=True)
if custom_cats:
    st.markdown(" ".join(f'<span class="badge badge-custom">{c}</span>' for c in custom_cats), unsafe_allow_html=True)
else:
    st.markdown('<span style="color:#7b7f96;font-size:0.85rem">None yet — add one below.</span>', unsafe_allow_html=True)

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
