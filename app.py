import streamlit as st
from theme import apply_theme, theme_toggle

st.set_page_config(page_title="Budget Tracker", page_icon="💸", layout="wide")
apply_theme()

# ── GUARD: already logged in → go straight to tracker ─────────────────────────
if "username" in st.session_state:
    st.switch_page("pages/tracker.py")

# ── TOGGLE ────────────────────────────────────────────────────────────────────
tcol1, tcol2 = st.columns([6, 1])
with tcol2:
    theme_toggle()

# ── LANDING ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:3rem 0 2rem;">
  <div class="title-gradient" style="font-size:3rem;">
    💸 Budget Tracker
  </div>
  <div class="subtitle" style="margin-top:0.5rem;">
    Track your spending. Own your money.
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Sign In", use_container_width=True):
        st.switch_page("pages/login.py")

col4, col5, col6 = st.columns([2, 1, 2])
with col5:
    st.markdown('<div style="text-align:center;color:var(--muted);font-size:0.8rem;margin-top:0.5rem;">No account? <a href="/register" style="color:var(--accent);">Register here</a></div>', unsafe_allow_html=True)
