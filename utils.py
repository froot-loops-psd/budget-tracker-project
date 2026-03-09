import hashlib
import gspread
import streamlit as st


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@st.cache_resource
def connect_gsheet():
    gc = gspread.service_account_from_dict(st.secrets["google_service_account"])
    return gc.open("Budget Control")