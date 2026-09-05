import streamlit as st
from utils import connect_gsheet
from services.auth_services import reset_password
from theme import apply_theme, theme_toggle

st.set_page_config(page_title="Reset Password", page_icon="🔑", layout="centered")
apply_theme()

tcol1, tcol2 = st.columns([3, 1])
with tcol2:
    theme_toggle()

st.markdown('<h1 class="title-gradient" style="text-align:center;">🔑 Reset Password</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="text-align:center;margin-bottom:2rem;">Enter your username and new password</p>', unsafe_allow_html=True)

sh = connect_gsheet()
user_ws = sh.worksheet("users")

username     = st.text_input("Username")
new_password = st.text_input("New Password", type="password")
confirm_pw   = st.text_input("Confirm New Password", type="password")

if st.button("Reset Password", use_container_width=True):
    if not username or not new_password:
        st.error("All fields are required.")
    elif new_password != confirm_pw:
        st.error("Passwords do not match.")
    elif len(new_password) < 6:
        st.error("Password must be at least 6 characters.")
    else:
        ok, msg = reset_password(user_ws, username, new_password)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

st.markdown("---")
if st.button("← Back to Login", use_container_width=True):
    st.switch_page("pages/login.py")
