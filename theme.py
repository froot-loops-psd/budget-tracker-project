"""Shared theme + styling for every page: one palette, one CSS block, one toggle."""
import streamlit as st

PALETTES = {
    "dark": dict(
        bg="#0e0f13", surface="#16181f", card="#1c1f2a", border="#2a2d3a",
        accent="#7c6af7", accent2="#f97c6a", green="#4ade80", red="#f87171",
        yellow="#facc15", text="#e8eaf2", muted="#7b7f96",
        shadow="0 8px 24px rgba(0,0,0,0.35)",
    ),
    "light": dict(
        bg="#f3f4f9", surface="#ffffff", card="#ffffff", border="#e1e3ee",
        accent="#7c6af7", accent2="#e8633f", green="#16a34a", red="#dc2626",
        yellow="#b45309", text="#1c1f2a", muted="#63667a",
        shadow="0 8px 24px rgba(30,32,60,0.08)",
    ),
}


def theme_mode() -> str:
    return st.session_state.get("theme_mode", "dark")


def apply_theme():
    """Inject the full theme CSS for the current mode. Call once near the top of every page."""
    p = PALETTES[theme_mode()]
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        --bg: {p['bg']}; --surface: {p['surface']}; --card: {p['card']}; --border: {p['border']};
        --accent: {p['accent']}; --accent2: {p['accent2']};
        --green: {p['green']}; --red: {p['red']}; --yellow: {p['yellow']};
        --text: {p['text']}; --muted: {p['muted']}; --shadow: {p['shadow']};
    }}

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }}

    h1, h2, h3 {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; }}

    header[data-testid="stHeader"] {{ display:none; }}
    #MainMenu, footer {{ display:none; }}
    [data-testid="stSidebarCollapsedControl"] {{ display:none; }}
    section[data-testid="stSidebar"] {{ display:none; }}
    [data-testid="stDecoration"] {{ display:none; }}

    .block-container {{ padding: 2rem 2.5rem; }}

    .title-gradient {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }}
    .subtitle {{ color: var(--muted); font-size: 0.88rem; }}

    .kpi-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); }}
    .kpi-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
    }}
    .kpi-label {{
        font-size: 0.68rem; color: var(--muted); text-transform: uppercase;
        letter-spacing: 0.12em; margin-bottom: 0.35rem; font-weight: 600;
    }}
    .kpi-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: clamp(1rem, 1.8vw, 1.4rem); font-weight: 700; color: var(--text);
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .kpi-sub {{ font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem; }}

    .empty-state {{
        background: var(--card); border: 1px dashed var(--border); border-radius: 14px;
        padding: 2rem 1.5rem; text-align: center; color: var(--muted); font-size: 0.88rem;
    }}
    .empty-state .icon {{ font-size: 1.6rem; margin-bottom: 0.4rem; }}

    .progress-wrap {{ background: var(--border); border-radius: 99px; height: 8px; margin: 0.5rem 0; }}
    .progress-fill {{ height: 8px; border-radius: 99px; transition: width 0.4s; }}

    button[data-baseweb="tab"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.82rem !important; font-weight: 600 !important; color: var(--muted) !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important; border-bottom-color: var(--accent) !important;
    }}

    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div,
    [data-testid="stDateInputField"] {{
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: 10px !important; color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    [data-testid="stDateInputField"] * {{ color: var(--text) !important; }}

    .stButton>button, .stFormSubmitButton>button {{
        background: linear-gradient(135deg, var(--accent), #6254d4) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 600 !important;
        font-size: 0.85rem !important; padding: 0.5rem 1.2rem !important;
        transition: opacity 0.2s, transform 0.15s;
    }}
    .stButton>button:hover, .stFormSubmitButton>button:hover {{ opacity: 0.85 !important; transform: translateY(-1px); }}

    .stDataFrame {{ border-radius: 12px; overflow: hidden; }}
    [data-testid="stMetricDelta"] {{ display:none; }}
    .stAlert {{ border-radius: 10px !important; }}
    hr {{ border-color: var(--border); }}

    .badge {{
        display: inline-block; background: var(--card); border: 1px solid var(--border);
        border-radius: 99px; padding: 0.2rem 0.7rem; font-size: 0.73rem;
        color: var(--muted); margin: 0.15rem;
    }}
    .badge-custom {{ border-color: var(--accent); color: var(--accent); }}
    </style>
    """, unsafe_allow_html=True)


def theme_toggle(container=None):
    """Render the light/dark toggle button. Pass a column/container to place it precisely."""
    target = container if container is not None else st
    mode = theme_mode()
    label = "🌙 Dark mode" if mode == "light" else "☀️ Light mode"
    if target.button(label, key="theme_toggle_btn", use_container_width=True):
        st.session_state.theme_mode = "light" if mode == "dark" else "dark"
        st.rerun()


def bar_color(pct: float) -> str:
    p = PALETTES[theme_mode()]
    return p["green"] if pct < 75 else (p["yellow"] if pct < 90 else p["red"])
