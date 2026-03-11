import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from services.sheet_services import get_sheet, ensure_sheet
from services.category_services import get_user_categories, add_category, delete_category, DEFAULT_CATEGORIES
from services.budget_services import get_budget, set_budget, update_budget
from services.expense_services import get_user_expenses, add_expense, auto_archive

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Budget Tracker", layout="wide", page_icon="💸")

# ── THEME ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0e0f13;
    --surface: #16181f;
    --card: #1c1f2a;
    --border: #2a2d3a;
    --accent: #7c6af7;
    --accent2: #f97c6a;
    --green: #4ade80;
    --red: #f87171;
    --text: #e8eaf2;
    --muted: #7b7f96;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

h1, h2, h3 {font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800;}

header[data-testid="stHeader"] {display:none;}
#MainMenu, footer {display:none;}
[data-testid="stSidebarCollapsedControl"] {display:none;}
section[data-testid="stSidebar"] {display:none;}

.block-container {padding: 2rem 2.5rem;}

.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-label {
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.35rem;
    font-weight: 600;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: clamp(1rem, 1.8vw, 1.4rem);
    font-weight: 700;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-sub {font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem;}

.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c6af7, #f97c6a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.page-sub {color: var(--muted); font-size: 0.82rem; margin-bottom: 1.5rem;}

.progress-wrap {background: var(--border); border-radius: 99px; height: 8px; margin: 0.5rem 0;}
.progress-fill {height: 8px; border-radius: 99px; transition: width 0.4s;}

button[data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stButton>button {
    background: linear-gradient(135deg, var(--accent), #6254d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.2s;
}
.stButton>button:hover {opacity: 0.85 !important;}

.stDataFrame {border-radius: 12px; overflow: hidden;}
[data-testid="stMetricDelta"] {display:none;}
.stAlert {border-radius: 10px !important;}
hr {border-color: var(--border);}

.badge {
    display: inline-block;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 0.2rem 0.7rem;
    font-size: 0.73rem;
    color: var(--muted);
    margin: 0.15rem;
}
</style>
""", unsafe_allow_html=True)

# ── GUARD ─────────────────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.warning("🔒 Please login first.")
    st.stop()

USERNAME = st.session_state["username"]
TODAY = datetime.now()
CURRENT_MONTH = TODAY.strftime("%Y-%m")

# ── SHEETS ────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_sheets():
    sh = get_sheet()
    expense_ws  = ensure_sheet(sh, "Daily Log", ["Username","Description","Amount","Category","Date","Month"])
    archive_ws  = ensure_sheet(sh, "Archive",   ["Username","Description","Amount","Category","Date","Month"])
    budget_ws   = ensure_sheet(sh, "Budget",    ["Username","Month","Budget"])
    category_ws = ensure_sheet(sh, "Categories",["Username","CategoryName"])
    return sh, expense_ws, archive_ws, budget_ws, category_ws

sh, expense_ws, archive_ws, budget_ws, category_ws = init_sheets()

auto_archive(expense_ws, archive_ws, CURRENT_MONTH)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df             = get_user_expenses(expense_ws, USERNAME)
arch_df        = get_user_expenses(archive_ws, USERNAME)
current_budget = get_budget(budget_ws, USERNAME, CURRENT_MONTH) or 0.0

this_month_df = df[df["Month"] == CURRENT_MONTH] if not df.empty and "Month" in df.columns else pd.DataFrame()
total_spent   = float(this_month_df["Amount"].sum()) if not this_month_df.empty else 0.0
remaining     = current_budget - total_spent
pct_used      = (total_spent / current_budget * 100) if current_budget > 0 else 0

# ── HEADER ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    st.markdown(f'<div class="page-title">💸 Budget Tracker</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Signed in as <b>{USERNAME}</b> · {TODAY.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
with col_h2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# ── KPI ROW ───────────────────────────────────────────────────────────────────
bar_color = "#4ade80" if pct_used < 75 else ("#facc15" if pct_used < 90 else "#f87171")
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, sub=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

kpi(k1, "Monthly Budget",  f"Rp {current_budget:,.0f}", CURRENT_MONTH)
kpi(k2, "Total Spent",     f"Rp {total_spent:,.0f}",    f"{len(this_month_df)} transactions")
kpi(k3, "Remaining",       f"Rp {remaining:,.0f}",       f"{100-pct_used:.1f}% left")
kpi(k4, "Usage",           f"{pct_used:.1f}%",           "of monthly budget")

st.markdown(f"""
<div class="progress-wrap">
  <div class="progress-fill" style="width:{min(pct_used,100):.1f}%;background:{bar_color};"></div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["💰 Budget", "🧾 Add Expense", "📈 Summary", "📚 History", "🏷️ Categories"])

# ═══════ TAB 0 — BUDGET ═══════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("Monthly Budget")
    if current_budget > 0:
        new_val = st.number_input("Update budget (Rp)", min_value=0, value=int(current_budget), step=50_000)
        if st.button("💾 Update Budget"):
            update_budget(budget_ws, USERNAME, CURRENT_MONTH, new_val)
            st.cache_resource.clear()
            st.success("Budget updated!")
            st.rerun()
    else:
        st.info("No budget set for this month yet.")
        init_val = st.number_input("Set initial budget (Rp)", min_value=0, step=50_000)
        if st.button("✅ Create Budget"):
            set_budget(budget_ws, USERNAME, CURRENT_MONTH, init_val)
            st.cache_resource.clear()
            st.success("Budget created!")
            st.rerun()

# ═══════ TAB 1 — ADD EXPENSE ══════════════════════════════════════════════════
with tabs[1]:
    st.subheader("Record a New Expense")

    if current_budget == 0:
        st.warning("⚠️ Please set a budget for this month before adding expenses.")
    else:
        categories = get_user_categories(category_ws, USERNAME)
        default_idx = categories.index("Other") if "Other" in categories else 0

        with st.form("expense_form", clear_on_submit=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                desc = st.text_input("Description *")
            with c2:
                amt = st.number_input("Amount (Rp) *", min_value=0, step=1_000)

            c3, c4 = st.columns(2)
            with c3:
                cat = st.selectbox("Category *", categories, index=default_idx)
            with c4:
                date_input = st.date_input("Date", value=TODAY.date())

            submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)

        if submitted:
            errors = []
            if not desc.strip():
                errors.append("Description is required.")
            if amt <= 0:
                errors.append("Amount must be greater than 0.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                add_expense(
                    expense_ws, USERNAME,
                    desc.strip(), amt, cat,
                    date_input.strftime("%Y-%m-%d"),
                    date_input.strftime("%Y-%m"),
                )
                st.cache_resource.clear()
                st.success(f"✅ Recorded: {desc.strip()} — Rp {amt:,.0f}")
                st.rerun()

        if not this_month_df.empty:
            st.markdown("#### Recent (This Month)")
            display = (
                this_month_df
                .sort_values("Date", ascending=False)
                .head(10)[["Date","Description","Category","Amount"]]
                .copy()
            )
            display["Date"] = display["Date"].dt.strftime("%d %b")
            display["Amount"] = display["Amount"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(display, use_container_width=True, hide_index=True)

# ═══════ TAB 2 — SUMMARY ══════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("Multi-Month Summary")

    combined = pd.concat([arch_df, df], ignore_index=True) if not df.empty or not arch_df.empty else pd.DataFrame()

    if combined.empty:
        st.info("No data yet.")
    else:
        combined = combined[combined["Username"] == USERNAME].copy() if "Username" in combined.columns else combined
        if "Month" not in combined.columns and "Date" in combined.columns:
            combined["Month"] = combined["Date"].dt.strftime("%Y-%m")

        monthly_sum = combined.groupby("Month", as_index=False)["Amount"].sum().sort_values("Month")

        fig_line = px.line(
            monthly_sum, x="Month", y="Amount", markers=True,
            title="Monthly Spend Trend",
            color_discrete_sequence=["#7c6af7"],
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf2", title_font_size=15,
            xaxis=dict(gridcolor="#2a2d3a"), yaxis=dict(gridcolor="#2a2d3a"),
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("#### Category Breakdown by Month")
        cat_month = combined.groupby(["Month","Category"], as_index=False)["Amount"].sum()
        available_months = sorted(cat_month["Month"].unique(), reverse=True)
        month_pick = st.selectbox("Select Month", available_months)
        sel = cat_month[cat_month["Month"] == month_pick].sort_values("Amount", ascending=False)

        col_b, col_p = st.columns([3, 2])
        with col_b:
            fig_bar = px.bar(
                sel, x="Category", y="Amount", title=f"Spending — {month_pick}",
                color_discrete_sequence=["#7c6af7"],
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="#e8eaf2", xaxis=dict(gridcolor="#2a2d3a"),
                                  yaxis=dict(gridcolor="#2a2d3a"))
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_p:
            fig_pie = px.pie(
                sel, values="Amount", names="Category", title="Category Share",
                color_discrete_sequence=px.colors.sequential.Purpor,
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e8eaf2")
            st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander("📋 Raw Data"):
            st.dataframe(combined.sort_values(["Month","Date"]), use_container_width=True, hide_index=True)

# ═══════ TAB 3 — HISTORY ══════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("Archive — Past Months")

    if arch_df.empty:
        st.info("No archived data yet.")
    else:
        months = sorted(arch_df["Month"].dropna().unique(), reverse=True) if "Month" in arch_df.columns else []
        if not months:
            st.info("No archive months found.")
        else:
            month_sel = st.selectbox("Select archived month", months)
            view = arch_df[arch_df["Month"] == month_sel].sort_values("Date", ascending=False)

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Spent", f"Rp {float(view['Amount'].sum()):,.0f}")
            m2.metric("Transactions", len(view))
            m3.metric("Categories Used", view["Category"].nunique())

            st.dataframe(view[["Date","Description","Category","Amount"]], use_container_width=True, hide_index=True)

# ═══════ TAB 4 — CATEGORIES ═══════════════════════════════════════════════════
with tabs[4]:
    st.subheader("Manage Categories")

    all_cats    = get_user_categories(category_ws, USERNAME)
    custom_cats = [c for c in all_cats if c not in DEFAULT_CATEGORIES]

    st.markdown("**Default categories** (cannot be deleted):")
    st.markdown(" ".join(f'<span class="badge">{c}</span>' for c in DEFAULT_CATEGORIES), unsafe_allow_html=True)

    st.markdown("<br>**Your custom categories:**", unsafe_allow_html=True)
    if custom_cats:
        st.markdown(" ".join(f'<span class="badge">{c}</span>' for c in custom_cats), unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#7b7f96;font-size:0.85rem">None yet.</span>', unsafe_allow_html=True)

    st.markdown("---")
    col_add, col_del = st.columns(2)

    with col_add:
        st.markdown("#### ➕ Add Category")
        with st.form("add_cat_form", clear_on_submit=True):
            new_cat = st.text_input("New category name")
            if st.form_submit_button("Add", use_container_width=True):
                nc = new_cat.strip()
                if not nc:
                    st.error("Name cannot be blank.")
                elif nc in all_cats:
                    st.warning("Category already exists.")
                else:
                    add_category(category_ws, USERNAME, nc)
                    st.success(f'"{nc}" added!')
                    st.rerun()

    with col_del:
        st.markdown("#### 🗑️ Delete Custom Category")
        if custom_cats:
            with st.form("del_cat_form"):
                del_choice = st.selectbox("Choose to delete", ["-"] + custom_cats)
                if st.form_submit_button("Delete", use_container_width=True):
                    if del_choice == "-":
                        st.info("Pick a category first.")
                    else:
                        deleted = delete_category(category_ws, USERNAME, del_choice)
                        if deleted:
                            st.success(f'"{del_choice}" deleted.')
                            st.rerun()
        else:
            st.info("No custom categories to delete.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("💾 Data stored in Google Sheets · Auto-archived monthly · Built with Streamlit")
