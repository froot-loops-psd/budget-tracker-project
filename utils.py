import hashlib
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def connect_gsheet():  # cached — one connection per app lifetime
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open("Budget Tracker")
    return sh

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
