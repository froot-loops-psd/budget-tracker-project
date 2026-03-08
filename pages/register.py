import streamlit as st
from utils import connect_gsheet
from services.auth_services import register_user

st.set_page_config(page_title="Register", page_icon="📝", layout="centered")

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

st.markdown('<h1 style="text-align:center;">📝 Create Account</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#7b7f96;margin-bottom:2rem;">Set up your budget tracker</p>', unsafe_allow_html=True)

sh = connect_gsheet()
user_ws = sh.worksheet("users")

new_username = st.text_input("Choose a Username")
new_password = st.text_input("Choose a Password", type="password")
confirm_pw   = st.text_input("Confirm Password", type="password")

if st.button("Create Account"):
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
if st.button("← Back to Login"):
    st.switch_page("pages/login.py")
