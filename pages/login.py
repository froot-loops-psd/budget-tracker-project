import streamlit as st
from utils import connect_gsheet
from services.auth_services import verify_login

st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400&display=swap');
html,body,[class*="css"]{background:#0e0f13;color:#e8eaf2;font-family:'DM Mono',monospace;}
h1,h2{font-family:'Syne',sans-serif;font-weight:800;}
header[data-testid="stHeader"],footer,#MainMenu{display:none;}
.stTextInput>div>div>input{background:#1c1f2a!important;border:1px solid #2a2d3a!important;border-radius:10px!important;color:#e8eaf2!important;}
.stButton>button{background:linear-gradient(135deg,#7c6af7,#6254d4)!important;color:white!important;border:none!important;border-radius:10px!important;width:100%;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center;background:linear-gradient(135deg,#7c6af7,#f97c6a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">💸 Budget Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#7b7f96;margin-bottom:2rem;">Sign in to your account</p>', unsafe_allow_html=True)

sh = connect_gsheet()
user_ws = sh.worksheet("users")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Sign In"):
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
    if st.button("Create Account"):
        st.switch_page("pages/register.py")
with col2:
    if st.button("Forgot Password"):
        st.switch_page("pages/reset_password.py")
