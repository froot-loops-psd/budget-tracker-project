import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from services.sheet_services import get_sheet, ensure_sheet
from services.category_services import get_user_categories, add_category, delete_category, DEFAULT_CATEGORIES
from services.budget_services import get_budget, set_budget, update_budget
from services.expense_services import get_user_expenses, add_expense, auto_archive
from services.savings_services import get_savings, get_monthly_savings, set_savings, update_savings
from services.investing_services import get_investments, add_investment
from theme import apply_theme, theme_toggle, bar_color, ring, PALETTES, theme_mode

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Budget Tracker", layout="wide", page_icon="💸")
apply_theme(sidebar=True)
PAL = PALETTES[theme_mode()]


def style_chart(fig):
    """Apply theme-aware colors so Plotly charts stay legible in both light and dark mode."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=PAL["text"],
        xaxis=dict(gridcolor=PAL["border"]), yaxis=dict(gridcolor=PAL["border"]),
        legend_title_text="",
    )
    return fig


def empty_state(icon, text):
    st.markdown(f"""
    <div class="empty-state">
        <div class="icon">{icon}</div>
        {text}
    </div>""", unsafe_allow_html=True)


def kpi(col, label, value, sub=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)


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

# auto_archive hits the Sheets API directly (uncached) — the sidebar nav triggers a
# full rerun on every click (unlike the old st.tabs, which never reran the script),
# so this must run at most once per session or it burns through the API rate limit.
if st.session_state.get("_auto_archived_month") != CURRENT_MONTH:
    auto_archive(expense_ws, archive_ws, CURRENT_MONTH)
    st.session_state["_auto_archived_month"] = CURRENT_MONTH

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df             = get_user_expenses(expense_ws, USERNAME)
arch_df        = get_user_expenses(archive_ws, USERNAME)
current_budget = get_budget(budget_ws, USERNAME, CURRENT_MONTH) or 0.0

this_month_df = df[df["Month"] == CURRENT_MONTH] if not df.empty and "Month" in df.columns else pd.DataFrame()
total_spent   = float(this_month_df["Amount"].sum()) if not this_month_df.empty else 0.0
remaining     = current_budget - total_spent
pct_used      = (total_spent / current_budget * 100) if current_budget > 0 else 0

saved_amt, saved_goal = get_monthly_savings(savings_ws, USERNAME, CURRENT_MONTH)
pct_saved = min((saved_amt or 0) / saved_goal * 100, 100) if saved_goal else 0

inv_df         = get_investments(investing_ws, USERNAME)
total_invested = float(inv_df["Amount"].sum()) if not inv_df.empty else 0.0
total_return   = float(inv_df["Return"].sum()) if not inv_df.empty else 0.0
net_value      = total_invested + total_return
ret_pct        = (total_return / total_invested * 100) if total_invested > 0 else 0

# ── SIDEBAR NAV ───────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("overview", "🏠", "Overview"),
    ("transactions", "🧾", "Transactions"),
    ("analytics", "📈", "Analytics"),
    ("budget", "💰", "Budget"),
    ("savings", "🏦", "Savings"),
    ("investing", "📊", "Investing"),
    ("categories", "🏷️", "Categories"),
]
if "nav_section" not in st.session_state:
    st.session_state.nav_section = "overview"

with st.sidebar:
    st.markdown('<div class="nav-brand">💸 Budget Tracker</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle' style='padding:0 0.4rem 1rem;'>Hi, <b>{USERNAME}</b></div>", unsafe_allow_html=True)
    for key, icon, label in NAV_ITEMS:
        is_active = st.session_state.nav_section == key
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.nav_section = key
            st.rerun()
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    theme_toggle(st.sidebar)
    if st.sidebar.button("🚪  Logout", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.switch_page("app.py")

section = st.session_state.nav_section
SECTION_TITLES = {key: label for key, _, label in NAV_ITEMS}

st.markdown(f'<div class="title-gradient" style="font-size:1.7rem;">{SECTION_TITLES[section]}</div>', unsafe_allow_html=True)
st.markdown(f"<div class='subtitle' style='margin-bottom:1.5rem;'>{TODAY.strftime('%A, %d %B %Y')} · {CURRENT_MONTH}</div>", unsafe_allow_html=True)

# ═══════ OVERVIEW ═════════════════════════════════════════════════════════════
if section == "overview":
    col_r1, col_r2, col_stats = st.columns([1.1, 1.1, 2.2])
    with col_r1:
        st.markdown(ring(pct_used, f"{pct_used:.0f}%", "budget used", color=bar_color(pct_used)), unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;margin-top:0.6rem;font-size:0.78rem;color:var(--muted);'>Rp {total_spent:,.0f} of Rp {current_budget:,.0f}</div>", unsafe_allow_html=True)
    with col_r2:
        st.markdown(ring(pct_saved, f"{pct_saved:.0f}%", "savings goal", color=PAL["accent2"]), unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;margin-top:0.6rem;font-size:0.78rem;color:var(--muted);'>Rp {(saved_amt or 0):,.0f} of Rp {(saved_goal or 0):,.0f}</div>", unsafe_allow_html=True)
    with col_stats:
        s1, s2 = st.columns(2, gap="medium")
        kpi(s1, "Remaining Budget", f"Rp {remaining:,.0f}", f"{100-pct_used:.1f}% left this month")
        kpi(s2, "Portfolio Value", f"Rp {net_value:,.0f}", f"{ret_pct:+.1f}% return")
        s3, s4 = st.columns(2, gap="medium")
        kpi(s3, "Transactions", str(len(this_month_df)), "this month")
        kpi(s4, "Categories Used", str(this_month_df["Category"].nunique()) if not this_month_df.empty else "0", "this month")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### Recent Activity")
    if this_month_df.empty:
        empty_state("🧾", "No transactions yet this month — head to Transactions to log one.")
    else:
        recent = this_month_df.sort_values("Date", ascending=False).head(6)
        for _, row in recent.iterrows():
            st.markdown(f"""
            <div class="activity-item">
                <div>
                    <div class="activity-desc">{row['Description']}</div>
                    <div class="activity-meta">{row['Category']} · {row['Date'].strftime('%d %b')}</div>
                </div>
                <div class="activity-amt">Rp {row['Amount']:,.0f}</div>
            </div>""", unsafe_allow_html=True)

# ═══════ TRANSACTIONS (Add Expense + This Month + Archive) ═══════════════════
elif section == "transactions":
    with st.expander("➕ Record a new expense", expanded=current_budget > 0 and this_month_df.empty):
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

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    view_choice = st.radio("View", ["This Month", "Archive"], horizontal=True, label_visibility="collapsed")

    if view_choice == "This Month":
        if this_month_df.empty:
            empty_state("🧾", "No transactions yet this month.")
        else:
            display = (
                this_month_df
                .sort_values("Date", ascending=False)[["Date","Description","Category","Amount"]]
                .copy()
            )
            display["Date"] = display["Date"].dt.strftime("%d %b")
            display["Amount"] = display["Amount"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        if arch_df.empty:
            empty_state("🗂️", "No archived data yet — past months are auto-archived here.")
        else:
            months = sorted(arch_df["Month"].dropna().unique(), reverse=True) if "Month" in arch_df.columns else []
            if not months:
                empty_state("🗂️", "No archive months found.")
            else:
                month_sel = st.selectbox("Select archived month", months)
                view = arch_df[arch_df["Month"] == month_sel].sort_values("Date", ascending=False)

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Spent", f"Rp {float(view['Amount'].sum()):,.0f}")
                m2.metric("Transactions", len(view))
                m3.metric("Categories Used", view["Category"].nunique())

                st.dataframe(view[["Date","Description","Category","Amount"]], use_container_width=True, hide_index=True)

# ═══════ ANALYTICS (formerly Summary) ═════════════════════════════════════════
elif section == "analytics":
    combined = pd.concat([arch_df, df], ignore_index=True) if not df.empty or not arch_df.empty else pd.DataFrame()

    if combined.empty:
        empty_state("📈", "No data yet — expenses you log will show up here as trends.")
    else:
        combined = combined[combined["Username"] == USERNAME].copy() if "Username" in combined.columns else combined
        if "Month" not in combined.columns and "Date" in combined.columns:
            combined["Month"] = combined["Date"].dt.strftime("%Y-%m")

        monthly_sum = combined.groupby("Month", as_index=False)["Amount"].sum().sort_values("Month")

        fig_line = px.line(
            monthly_sum, x="Month", y="Amount", markers=True,
            title="Monthly Spend Trend",
            color_discrete_sequence=[PAL["accent"]],
        )
        style_chart(fig_line).update_layout(title_font_size=15)
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
                color_discrete_sequence=[PAL["accent"]],
            )
            style_chart(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_p:
            fig_pie = px.pie(
                sel, values="Amount", names="Category", title="Category Share",
                color_discrete_sequence=px.colors.sequential.Emrld,
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=PAL["text"])
            st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander("📋 Raw Data"):
            st.dataframe(combined.sort_values(["Month","Date"]), use_container_width=True, hide_index=True)

# ═══════ BUDGET ════════════════════════════════════════════════════════════════
elif section == "budget":
    col_r, col_form = st.columns([1, 2], gap="large")
    with col_r:
        st.markdown(ring(pct_used, f"{pct_used:.0f}%", "used", color=bar_color(pct_used), size=150), unsafe_allow_html=True)
    with col_form:
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

# ═══════ SAVINGS ═══════════════════════════════════════════════════════════════
elif section == "savings":
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

    if saved_goal and saved_goal > 0:
        sav_col = "var(--green)" if pct_saved >= 100 else ("var(--yellow)" if pct_saved >= 50 else "var(--accent2)")
        st.markdown(f"""
        <div style="margin:1rem 0 0.3rem;font-size:0.82rem;color:var(--muted);">
            Progress: <b style="color:var(--text)">Rp {(saved_amt or 0):,.0f}</b> of
            <b style="color:var(--text)">Rp {saved_goal:,.0f}</b> goal ({pct_saved:.1f}%)
        </div>
        <div class="progress-wrap">
          <div class="progress-fill" style="width:{pct_saved:.1f}%;background:{sav_col};"></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Savings Over Time")
    sav_df = get_savings(savings_ws, USERNAME)
    if not sav_df.empty:
        sav_df = sav_df.sort_values("Month")
        fig_sav = px.bar(
            sav_df, x="Month", y=["Amount", "Goal"],
            barmode="group", title="Monthly Savings vs Goal",
            color_discrete_map={"Amount": PAL["accent"], "Goal": PAL["border"]},
        )
        style_chart(fig_sav)
        st.plotly_chart(fig_sav, use_container_width=True)
    else:
        empty_state("🏦", "No savings data yet — set an amount above to start tracking.")

# ═══════ INVESTING ═════════════════════════════════════════════════════════════
elif section == "investing":
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

    if not inv_df.empty:
        st.markdown("---")
        ret_color = PAL["green"] if total_return >= 0 else PAL["red"]

        pm1, pm2, pm3, pm4 = st.columns(4)
        kpi(pm1, "Total Invested",  f"Rp {total_invested:,.0f}")
        kpi(pm2, "Total Return",    f'<span style="color:{ret_color}">Rp {total_return:,.0f}</span>', f"{ret_pct:+.1f}%")
        kpi(pm3, "Portfolio Value", f"Rp {net_value:,.0f}")
        kpi(pm4, "Assets Tracked",  str(inv_df["Ticker"].nunique()), "unique tickers")

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
                color_discrete_map={"Invested": PAL["accent"], "Return": PAL["green"]},
            )
            style_chart(fig_inv)
            st.plotly_chart(fig_inv, use_container_width=True)
        with ct2:
            fig_pie_inv = px.pie(
                by_ticker, values="Invested", names="Ticker",
                title="Portfolio Allocation",
                color_discrete_sequence=px.colors.sequential.Emrld,
            )
            fig_pie_inv.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=PAL["text"])
            st.plotly_chart(fig_pie_inv, use_container_width=True)

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
                "Cumulative Invested": PAL["muted"],
                "Portfolio Value":     PAL["accent"],
            },
        )
        style_chart(fig_growth)
        st.plotly_chart(fig_growth, use_container_width=True)

        with st.expander("📋 All Entries"):
            display_inv = inv_df.copy()
            if "Date" in display_inv.columns:
                display_inv["Date"] = display_inv["Date"].dt.strftime("%d %b %Y")
            st.dataframe(
                display_inv[["Date","Ticker","Amount","Return","Month"]],
                use_container_width=True, hide_index=True
            )
    else:
        empty_state("📊", "No investment entries yet — add one above to start tracking your portfolio.")

# ═══════ CATEGORIES ════════════════════════════════════════════════════════════
elif section == "categories":
    col_cat_title, col_cat_link = st.columns([4, 1.6])
    with col_cat_link:
        if st.button("🏷️ Open full page", use_container_width=True):
            st.switch_page("pages/custom_category.py")

    all_cats    = get_user_categories(category_ws, USERNAME)
    custom_cats = [c for c in all_cats if c not in DEFAULT_CATEGORIES]

    st.markdown("**Default categories** (cannot be deleted):")
    st.markdown(" ".join(f'<span class="badge">{c}</span>' for c in DEFAULT_CATEGORIES), unsafe_allow_html=True)

    st.markdown("<br>**Your custom categories:**", unsafe_allow_html=True)
    if custom_cats:
        st.markdown(" ".join(f'<span class="badge">{c}</span>' for c in custom_cats), unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:var(--muted);font-size:0.85rem">None yet.</span>', unsafe_allow_html=True)

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
