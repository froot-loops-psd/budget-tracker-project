import streamlit as st

st.set_page_config(page_title="Budget Tracker", page_icon="💸", layout="wide")

# ── THEME ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400&display=swap');
html,body,[class*="css"]{background:#0e0f13;color:#e8eaf2;font-family:'DM Mono',monospace;}
header[data-testid="stHeader"],footer,#MainMenu{display:none;}
h1,h2{font-family:'Syne',sans-serif;font-weight:800;}
.stButton>button{
    background:linear-gradient(135deg,#7c6af7,#6254d4)!important;
    color:white!important;border:none!important;
    border-radius:10px!important;font-family:'DM Mono',monospace!important;
    width:100%;padding:0.6rem!important;
}
</style>
""", unsafe_allow_html=True)

# ── GUARD: already logged in → go straight to tracker ─────────────────────────
if "username" in st.session_state:
    st.switch_page("pages/tracker.py")

# ── LANDING ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:4rem 0 2rem;">
  <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
              background:linear-gradient(135deg,#7c6af7,#f97c6a);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    💸 Budget Tracker
  </div>
  <div style="color:#7b7f96;margin-top:0.5rem;font-size:0.9rem;">
    Track your spending. Own your money.
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Sign In"):
        st.switch_page("pages/login.py")

col4, col5, col6 = st.columns([2, 1, 2])
with col5:
    st.markdown('<div style="text-align:center;color:#7b7f96;font-size:0.8rem;margin-top:0.5rem;">No account? <a href="/register" style="color:#7c6af7;">Register here</a></div>', unsafe_allow_html=True)
