import streamlit as st
from utils import connect_gsheet
from services.auth_services import verify_login
from theme import apply_theme, theme_toggle

st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")
apply_theme()

tcol1, tcol2 = st.columns([3, 1])
with tcol2:
    theme_toggle()

st.markdown('<h1 class="title-gradient" style="text-align:center;">💸 Budget Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="text-align:center;margin-bottom:2rem;">Sign in to your account</p>', unsafe_allow_html=True)

sh = connect_gsheet()
user_ws = sh.worksheet("users")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Sign In", use_container_width=True):
    if not username or not password:
        st.error("Please fill in both fields.")
    elif verify_login(user_ws, username, password):
        st.session_state["username"] = username
        st.success(f"Welcome back, {username}!")
        st.switch_page("pages/tracker.py")
    else:
        st.error("Invalid username or password.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Create Account", use_container_width=True):
        st.switch_page("pages/register.py")
with col2:
    if st.button("Forgot Password", use_container_width=True):
        st.switch_page("pages/reset_password.py")
