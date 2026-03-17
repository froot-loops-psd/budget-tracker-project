import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from services.sheet_services import get_sheet, ensure_sheet
from services.category_services import get_user_categories, add_category, delete_category, DEFAULT_CATEGORIES
from services.budget_services import get_budget, set_budget, update_budget
from services.expense_services import get_user_expenses, add_expense, auto_archive
from services.savings_services import get_savings, get_monthly_savings, set_savings, update_savings
from services.investing_services import get_investments, add_investment

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
    expense_ws   = ensure_sheet(sh, "Daily Log",  ["Username","Description","Amount","Category","Date","Month"])
    archive_ws   = ensure_sheet(sh, "Archive",    ["Username","Description","Amount","Category","Date","Month"])
    budget_ws    = ensure_sheet(sh, "Budget",     ["Username","Month","Budget"])
    category_ws  = ensure_sheet(sh, "Categories", ["Username","CategoryName"])
    savings_ws   = ensure_sheet(sh, "Savings",    ["Username","Month","Amount","Goal"])
    investing_ws = ensure_sheet(sh, "Investing",  ["Username","Date","Month","Ticker","Amount","Return"])
    return sh, expense_ws, archive_ws, budget_ws, category_ws, savings_ws, investing_ws

sh, expense_ws, archive_ws, budget_ws, category_ws, savings_ws, investing_ws = init_sheets()

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
tabs = st.tabs(["💰 Budget", "🧾 Add Expense", "📈 Summary", "📚 History", "🏦 Savings", "📊 Investing", "🏷️ Categories"])

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

# ═══════ TAB 4 — SAVINGS ══════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("💰 Savings — " + CURRENT_MONTH)

    saved_amt, saved_goal = get_monthly_savings(savings_ws, USERNAME, CURRENT_MONTH)

    # ── Set / Update this month's savings ─────────────────────────────────────
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        new_amt  = st.number_input("Saved this month (Rp)", min_value=0, step=50_000,
                                   value=int(saved_amt) if saved_amt else 0)
    with col_s2:
        new_goal = st.number_input("Savings goal this month (Rp)", min_value=0, step=50_000,
                                   value=int(saved_goal) if saved_goal else 0)

    if st.button("💾 Save", key="save_savings"):
        if saved_amt is None:
            set_savings(savings_ws, USERNAME, CURRENT_MONTH, new_amt, new_goal)
        else:
            update_savings(savings_ws, USERNAME, CURRENT_MONTH, new_amt, new_goal)
        st.cache_resource.clear()
        st.success("Savings updated!")
        st.rerun()

    # ── Progress toward goal ───────────────────────────────────────────────────
    if saved_goal and saved_goal > 0:
        pct_saved = min((saved_amt or 0) / saved_goal * 100, 100)
        bar_col   = "#4ade80" if pct_saved >= 100 else ("#facc15" if pct_saved >= 50 else "#f97c6a")
        st.markdown(f"""
        <div style="margin:1rem 0 0.3rem;font-size:0.82rem;color:#7b7f96;">
            Progress: <b style="color:#e8eaf2">Rp {(saved_amt or 0):,.0f}</b> of
            <b style="color:#e8eaf2">Rp {saved_goal:,.0f}</b> goal ({pct_saved:.1f}%)
        </div>
        <div class="progress-wrap">
          <div class="progress-fill" style="width:{pct_saved:.1f}%;background:{bar_col};"></div>
        </div>""", unsafe_allow_html=True)

    # ── Historical savings chart ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Savings Over Time")
    sav_df = get_savings(savings_ws, USERNAME)
    if not sav_df.empty:
        sav_df = sav_df.sort_values("Month")
        fig_sav = px.bar(
            sav_df, x="Month", y=["Amount", "Goal"],
            barmode="group", title="Monthly Savings vs Goal",
            color_discrete_map={"Amount": "#7c6af7", "Goal": "#2a2d3a"},
        )
        fig_sav.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf2", xaxis=dict(gridcolor="#2a2d3a"),
            yaxis=dict(gridcolor="#2a2d3a"), legend_title_text="",
        )
        st.plotly_chart(fig_sav, use_container_width=True)
    else:
        st.info("No savings data yet.")

# ═══════ TAB 5 — INVESTING ════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("📊 Investing")

    # ── Add new investment ─────────────────────────────────────────────────────
    st.markdown("#### Add Investment Entry")
    with st.form("invest_form", clear_on_submit=True):
        ci1, ci2, ci3 = st.columns(3)
        with ci1:
            ticker    = st.text_input("Ticker / Asset (e.g. BBCA, BTC)").upper().strip()
        with ci2:
            inv_amt   = st.number_input("Amount Invested (Rp)", min_value=0, step=10_000)
        with ci3:
            inv_return = st.number_input("Return (Rp) — negative if loss", step=1_000)

        ci4, _ = st.columns([1, 2])
        with ci4:
            inv_date = st.date_input("Date", value=TODAY.date(), key="inv_date")

        inv_submit = st.form_submit_button("➕ Add Entry", use_container_width=True)

    if inv_submit:
        if not ticker:
            st.error("Ticker / asset name is required.")
        elif inv_amt <= 0:
            st.error("Amount must be greater than 0.")
        else:
            add_investment(
                investing_ws, USERNAME,
                inv_date.strftime("%Y-%m-%d"),
                inv_date.strftime("%Y-%m"),
                ticker, inv_amt, inv_return,
            )
            st.cache_resource.clear()
            st.success(f"✅ {ticker} — Rp {inv_amt:,.0f} added.")
            st.rerun()

    # ── Portfolio summary ──────────────────────────────────────────────────────
    inv_df = get_investments(investing_ws, USERNAME)

    if not inv_df.empty:
        st.markdown("---")
        total_invested = float(inv_df["Amount"].sum())
        total_return   = float(inv_df["Return"].sum())
        net_value      = total_invested + total_return
        ret_pct        = (total_return / total_invested * 100) if total_invested > 0 else 0
        ret_color      = "#4ade80" if total_return >= 0 else "#f87171"

        pm1, pm2, pm3, pm4 = st.columns(4)
        def inv_kpi(col, label, value, sub=""):
            col.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
            </div>""", unsafe_allow_html=True)

        inv_kpi(pm1, "Total Invested",  f"Rp {total_invested:,.0f}")
        inv_kpi(pm2, "Total Return",    f'<span style="color:{ret_color}">Rp {total_return:,.0f}</span>', f"{ret_pct:+.1f}%")
        inv_kpi(pm3, "Portfolio Value", f"Rp {net_value:,.0f}")
        inv_kpi(pm4, "Assets Tracked",  str(inv_df["Ticker"].nunique()), "unique tickers")

        # ── By ticker ─────────────────────────────────────────────────────────
        st.markdown("#### Portfolio Breakdown")
        by_ticker = (
            inv_df.groupby("Ticker", as_index=False)
            .agg(Invested=("Amount","sum"), Return=("Return","sum"))
        )
        by_ticker["Net"] = by_ticker["Invested"] + by_ticker["Return"]
        by_ticker["Return %"] = (by_ticker["Return"] / by_ticker["Invested"] * 100).round(2)

        ct1, ct2 = st.columns([3, 2])
        with ct1:
            fig_inv = px.bar(
                by_ticker, x="Ticker", y=["Invested", "Return"],
                barmode="group", title="Invested vs Return by Asset",
                color_discrete_map={"Invested": "#7c6af7", "Return": "#4ade80"},
            )
            fig_inv.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8eaf2", xaxis=dict(gridcolor="#2a2d3a"),
                yaxis=dict(gridcolor="#2a2d3a"), legend_title_text="",
            )
            st.plotly_chart(fig_inv, use_container_width=True)
        with ct2:
            fig_pie_inv = px.pie(
                by_ticker, values="Invested", names="Ticker",
                title="Portfolio Allocation",
                color_discrete_sequence=px.colors.sequential.Purpor,
            )
            fig_pie_inv.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e8eaf2")
            st.plotly_chart(fig_pie_inv, use_container_width=True)

        # ── Growth over time ──────────────────────────────────────────────────
        st.markdown("#### Growth Over Time")
        monthly_inv = inv_df.groupby("Month", as_index=False).agg(
            Invested=("Amount","sum"), Return=("Return","sum")
        ).sort_values("Month")
        monthly_inv["Cumulative Invested"] = monthly_inv["Invested"].cumsum()
        monthly_inv["Cumulative Return"]   = monthly_inv["Return"].cumsum()
        monthly_inv["Portfolio Value"]     = monthly_inv["Cumulative Invested"] + monthly_inv["Cumulative Return"]

        fig_growth = px.line(
            monthly_inv, x="Month",
            y=["Cumulative Invested", "Portfolio Value"],
            markers=True, title="Portfolio Growth",
            color_discrete_map={
                "Cumulative Invested": "#7b7f96",
                "Portfolio Value":     "#7c6af7",
            },
        )
        fig_growth.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf2", xaxis=dict(gridcolor="#2a2d3a"),
            yaxis=dict(gridcolor="#2a2d3a"), legend_title_text="",
        )
        st.plotly_chart(fig_growth, use_container_width=True)

        # ── Raw table ─────────────────────────────────────────────────────────
        with st.expander("📋 All Entries"):
            display_inv = inv_df.copy()
            if "Date" in display_inv.columns:
                display_inv["Date"] = display_inv["Date"].dt.strftime("%d %b %Y")
            st.dataframe(
                display_inv[["Date","Ticker","Amount","Return","Month"]],
                use_container_width=True, hide_index=True
            )
    else:
        st.info("No investment entries yet.")

# ═══════ TAB 6 — CATEGORIES ═══════════════════════════════════════════════════
with tabs[6]:
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
