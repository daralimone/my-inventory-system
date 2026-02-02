import streamlit as st
import sqlite3
import pandas as pd
import time
from extra_streamlit_components import CookieManager

# --- ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តុក", layout="wide")

# បង្កើត Cookie Manager
cookie_manager = CookieManager()

def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, price REAL)''')
    conn.commit()
    conn.close()

init_db()

def login():
    # ១. អានទិន្នន័យពី Secrets ដែលអ្នកបាន Save មិញ
    CORRECT_USER = st.secrets["credentials"]["username"]
    CORRECT_PASS = st.secrets["credentials"]["password"]

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # ២. ពិនិត្យ Cookie សម្រាប់ Refresh
    cookie_status = cookie_manager.get(cookie="is_logged_in")
    if cookie_status == "true":
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ចូលប្រើប្រាស់ប្រព័ន្ធ</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("ចូលប្រើ", use_container_width=True):
                if username == CORRECT_USER and password == CORRECT_PASS:
                    cookie_manager.set("is_logged_in", "true", max_age=86400)
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("ឈ្មោះ ឬ លេខកូដមិនត្រឹមត្រូវ!")
        return False
    return True

if login():
    st.title("📦 គ្រប់គ្រងស្តុករបស់អ្នក")
    # បញ្ចូលកូដបង្ហាញទិន្នន័យរបស់អ្នកបន្តនៅទីនេះ...