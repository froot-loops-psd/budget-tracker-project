"""Shared theme + styling for every page: one palette, one CSS block, one toggle."""
import streamlit as st

PALETTES = {
    "dark": dict(
        bg="#05070a", surface="#0d1117", card="#121722", card2="#171d2b", border="#232938",
        accent="#10b981", accent2="#f5a524", green="#34d399", red="#f87171",
        yellow="#fbbf24", text="#f1f5f9", muted="#8b93a7",
        shadow="0 8px 28px rgba(0,0,0,0.45)",
    ),
    "light": dict(
        bg="#f5f6fa", surface="#ffffff", card="#ffffff", card2="#f0f2f8", border="#e2e5ef",
        accent="#059669", accent2="#c2740a", green="#16a34a", red="#dc2626",
        yellow="#b45309", text="#0f172a", muted="#5b6072",
        shadow="0 8px 28px rgba(30,32,60,0.08)",
    ),
}


def theme_mode() -> str:
    return st.session_state.get("theme_mode", "dark")


def apply_theme(sidebar: bool = False):
    """Inject the full theme CSS for the current mode. Call once near the top of every page.

    sidebar=True keeps Streamlit's sidebar visible (for pages that use it as a nav rail)
    but still hides the auto-generated multipage link list inside it.
    """
    p = PALETTES[theme_mode()]
    if sidebar:
        # The sidebar-reopen button lives inside stHeader, so we can't display:none the
        # whole header here (that would remove the button from the render tree too).
        # Instead: collapse the header to zero height, hide its other contents, and pull
        # the reopen button out via fixed positioning so a zero-sized ancestor can't clip it.
        sidebar_css = """
        [data-testid="stSidebarNav"] { display:none; }
        header[data-testid="stHeader"] {
            height: 0 !important; min-height: 0 !important; overflow: visible !important;
            background: transparent !important; box-shadow: none !important;
        }
        [data-testid="stToolbarActions"], [data-testid="stMainMenu"],
        [data-testid="stAppDeployButton"], [data-testid="stHeaderActionElements"] { display:none !important; }
        [data-testid="stExpandSidebarButton"] {
            position: fixed !important; top: 0.6rem !important; left: 0.6rem !important;
            z-index: 999999 !important;
        }
        """
    else:
        sidebar_css = """
        header[data-testid="stHeader"] { display:none; }
        section[data-testid="stSidebar"] { display:none; }
        [data-testid="stExpandSidebarButton"] { display:none; }
        [data-testid="stSidebarCollapsedControl"] { display:none; }
        """
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {{
        --bg: {p['bg']}; --surface: {p['surface']}; --card: {p['card']}; --card2: {p['card2']}; --border: {p['border']};
        --accent: {p['accent']}; --accent2: {p['accent2']};
        --green: {p['green']}; --red: {p['red']}; --yellow: {p['yellow']};
        --text: {p['text']}; --muted: {p['muted']}; --shadow: {p['shadow']};
    }}

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        font-family: 'Sora', sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }}

    h1, h2, h3 {{ font-family: 'Sora', sans-serif; font-weight: 800; }}

    #MainMenu, footer {{ display:none; }}
    [data-testid="stDecoration"] {{ display:none; }}
    {sidebar_css}

    /* Re-open control for a collapsed sidebar (only relevant when sidebar=True) */
    [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] {{
        background: var(--card) !important; border-radius: 10px !important;
        top: 0.6rem !important; left: 0.6rem !important;
        min-width: 2.2rem !important; min-height: 2.2rem !important;
        padding: 0.4rem !important;
    }}
    [data-testid="stExpandSidebarButton"] svg, [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stExpandSidebarButton"] span, [data-testid="stSidebarCollapsedControl"] span {{
        color: var(--text) !important; fill: var(--text) !important;
    }}

    section[data-testid="stSidebar"] {{
        background: var(--surface);
        border-right: 1px solid var(--border);
    }}
    section[data-testid="stSidebar"] .stButton>button {{
        background: transparent !important; color: var(--muted) !important;
        border: none !important; box-shadow:none !important;
        font-weight: 600 !important; font-size: 0.86rem !important;
        text-align: left !important; justify-content: flex-start !important;
        padding: 0.55rem 0.8rem !important; border-radius: 10px !important;
        transition: background 0.15s, color 0.15s;
    }}
    section[data-testid="stSidebar"] .stButton>button:hover {{
        background: var(--card) !important; color: var(--text) !important; opacity:1 !important; transform:none !important;
    }}
    section[data-testid="stSidebar"] .stButton>button p {{ text-align: left !important; }}
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {{
        background: var(--card) !important; color: var(--accent) !important;
        border-left: 3px solid var(--accent) !important;
    }}

    .block-container {{ padding: 2rem 2.5rem; }}

    .title-gradient {{
        font-family: 'Sora', sans-serif;
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
        transition: transform 0.15s ease;
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
        font-family: 'IBM Plex Mono', monospace;
        font-size: clamp(1rem, 1.8vw, 1.4rem); font-weight: 600; color: var(--text);
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .kpi-sub {{ font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem; }}

    .hero-card {{
        background: var(--card); border: 1px solid var(--border); border-radius: 20px;
        padding: 1.5rem; box-shadow: var(--shadow); display:flex; align-items:center; gap:1.2rem;
    }}
    .activity-item {{
        display:flex; justify-content:space-between; align-items:center;
        padding: 0.65rem 0.2rem; border-bottom: 1px solid var(--border); font-size:0.86rem;
    }}
    .activity-item:last-child {{ border-bottom:none; }}
    .activity-desc {{ color: var(--text); font-weight:600; }}
    .activity-meta {{ color: var(--muted); font-size:0.75rem; }}
    .activity-amt {{ font-family:'IBM Plex Mono', monospace; font-weight:600; }}

    .empty-state {{
        background: var(--card); border: 1px dashed var(--border); border-radius: 14px;
        padding: 2rem 1.5rem; text-align: center; color: var(--muted); font-size: 0.88rem;
    }}
    .empty-state .icon {{ font-size: 1.6rem; margin-bottom: 0.4rem; }}

    .progress-wrap {{ background: var(--border); border-radius: 99px; height: 8px; margin: 0.5rem 0; }}
    .progress-fill {{ height: 8px; border-radius: 99px; transition: width 0.4s; }}

    .nav-brand {{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.2rem; padding: 0.4rem 0.4rem 1rem; }}
    .nav-section-label {{
        font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color: var(--muted);
        padding: 0.8rem 0.8rem 0.3rem; font-weight:700;
    }}

    div[data-baseweb="radio"] label {{
        background: var(--card); border:1px solid var(--border); border-radius: 10px !important;
        padding: 0.4rem 0.9rem !important; margin-right: 0.4rem !important; font-size:0.82rem !important;
    }}

    button[data-baseweb="tab"] {{
        font-family: 'Sora', sans-serif !important;
        font-size: 0.82rem !important; font-weight: 600 !important; color: var(--muted) !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important; border-bottom-color: var(--accent) !important;
    }}

    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div,
    [data-testid="stDateInputField"] {{
        background: var(--card2) !important; border: 1px solid var(--border) !important;
        border-radius: 10px !important; color: var(--text) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }}
    [data-testid="stDateInputField"] * {{ color: var(--text) !important; }}

    .stButton>button, .stFormSubmitButton>button {{
        background: linear-gradient(135deg, var(--accent), #0d9668) !important;
        color: #06120d !important; border: none !important; border-radius: 10px !important;
        font-family: 'Sora', sans-serif !important; font-weight: 700 !important;
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


def ring(pct: float, center_label: str, center_sub: str = "", color: str = None, size: int = 130, stroke: int = 12) -> str:
    """Circular progress ring as an HTML/CSS snippet (conic-gradient, no JS/canvas needed)."""
    p = PALETTES[theme_mode()]
    color = color or p["accent"]
    pct = max(0, min(pct, 100))
    deg = pct * 3.6
    inner = size - stroke * 2
    return f"""
    <div style="width:{size}px;height:{size}px;border-radius:50%;
                background:conic-gradient({color} {deg:.1f}deg, var(--border) {deg:.1f}deg 360deg);
                display:flex;align-items:center;justify-content:center;flex-shrink:0;">
        <div style="width:{inner}px;height:{inner}px;border-radius:50%;background:var(--card);
                    display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;">
            <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:1rem;color:var(--text);line-height:1.2;">{center_label}</div>
            <div style="font-size:0.62rem;color:var(--muted);margin-top:2px;">{center_sub}</div>
        </div>
    </div>
    """
