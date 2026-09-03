import streamlit as st
from utils import connect_gsheet
from services.auth_services import register_user
from theme import apply_theme, theme_toggle

st.set_page_config(page_title="Register", page_icon="📝", layout="centered")
apply_theme()

tcol1, tcol2 = st.columns([3, 1])
with tcol2:
    theme_toggle()

st.markdown('<h1 class="title-gradient" style="text-align:center;">📝 Create Account</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="text-align:center;margin-bottom:2rem;">Set up your budget tracker</p>', unsafe_allow_html=True)

sh = connect_gsheet()
user_ws = sh.worksheet("users")

new_username = st.text_input("Choose a Username")
new_password = st.text_input("Choose a Password", type="password")
confirm_pw   = st.text_input("Confirm Password", type="password")

if st.button("Create Account", use_container_width=True):
    if not new_username or not new_password:
        st.error("All fields are required.")
    elif new_password != confirm_pw:
        st.error("Passwords do not match.")
    elif len(new_password) < 6:
        st.error("Password must be at least 6 characters.")
    else:
        ok, msg = register_user(user_ws, new_username, new_password)
        if ok:
            st.success(msg)
            st.info("You can now sign in.")
        else:
            st.error(msg)

st.markdown("---")
if st.button("← Back to Login", use_container_width=True):
    st.switch_page("pages/login.py")
