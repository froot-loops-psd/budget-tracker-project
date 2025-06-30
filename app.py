import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

#Set Up Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

#Connect to Google Sheets
sheet = client.open("Budget Control").worksheet("Daily Log")

st.title("💸 Dava's Budget Tracker")

#Input Form
with st.form("expense_form"):
    description = st.text_input("Description")
    category = st.selectbox("Category", ["Liability", "Expense", "Cat", "Makanan", "Minuman", "Pleasure", "Transport", "Other"])
    amount = st.number_input("Amount (Rp)", min_value=0)
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        today = datetime.now().strftime('%Y-%m-%d')
        sheet.append_row([today, description, category, amount])
        st.success(f"✅ Expense added: {description} - {category} - Rp{amount}")

#Fetch Data to Summary
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    st.subheader("💰 Summary")
    total_expense = df['Amount'].sum()
    st.write(f"### Total Expense: Rp{total_expense:,.2f}:")

    st.subheader("📊 Expense by Category")
    category_summary = df.groupby('Category')['Amount'].sum().reset_index()
    st.bar_chart(category_summary, x='Category', y='Amount')

    #Special Tracker: Makanan, Minuman, dan Pleasure
    st.subheader("Makanan, Minuman, dan Pleasure Tracker")
    makanan_expense = df[df['Category'] == "Makanan"]['Amount'].sum()
    minuman_expense = df[df['Category'] == "Minuman"]['Amount'].sum()
    pleasure_expense = df[df['Category'] == "Pleasure"]['Amount'].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Makanan (Rp)", f"{makanan_expense:,.2f}")
    with col2:
        st.metric("Total Minuman (Rp)", f"{minuman_expense:,.2f}")
    with col3:
        st.metric("Total Pleasure (Rp)", f"{pleasure_expense:,.2f}")

    st.subheader("📅 Recent Expenses")
    st.dataframe(df.tail(20))

else:
    st.write("Belum ada data bro!")