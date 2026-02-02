import streamlit as st
import sqlite3
import pandas as pd
import time
from extra_streamlit_components import CookieManager

# --- ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តុក", layout="wide")
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
    try:
        CORRECT_USER = st.secrets["credentials"]["username"]
        CORRECT_PASS = st.secrets["credentials"]["password"]
    except:
        st.error("សូមកំណត់ Secrets ជាមុនសិន!")
        return False

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    cookie_status = cookie_manager.get(cookie="is_logged_in")
    if cookie_status == "true":
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ចូលប្រើប្រាស់ប្រព័ន្ធ</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("ចូលប្រើ", use_container_width=True):
                if u == CORRECT_USER and p == CORRECT_PASS:
                    cookie_manager.set("is_logged_in", "true", max_age=86400)
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("ខុសលេខកូដ!")
        return False
    return True

if login():
    if st.sidebar.button("ចាកចេញ (Log out)"):
        cookie_manager.delete("is_logged_in")
        st.session_state["logged_in"] = False
        st.rerun()

    st.title("📦 គ្រប់គ្រងស្តុក និងលក់ដូរ")

    # --- ១. ផ្នែកស្វែងរកទំនិញ ---
    search_query = st.text_input("🔍 ស្វែងរកទំនិញតាមឈ្មោះ...", "")

    # --- ២. Sidebar: បញ្ចូលទំនិញថ្មី ---
    st.sidebar.header("📝 បញ្ចូលទិន្នន័យ")
    with st.sidebar.form("add_form", clear_on_submit=True):
        name = st.text_input("ឈ្មោះទំនិញ")
        qty = st.number_input("ចំនួន", min_value=0)
        price = st.number_input("តម្លៃ ($)", min_value=0.0, format="%.2f")
        if st.form_submit_button("បញ្ចូលទៅក្នុងស្តុក"):
            if name:
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (name, qty, price))
                conn.commit()
                conn.close()
                st.rerun()

    # --- ៣. ទាញទិន្នន័យមកបង្ហាញ ---
    conn = sqlite3.connect('business.db')
    query = "SELECT * FROM products"
    if search_query:
        query = f"SELECT * FROM products WHERE name LIKE '%{search_query}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    st.subheader("📋 បញ្ជីទំនិញបច្ចុប្បន្ន")
    st.dataframe(df, use_container_width=True)

    # --- ៤. មុខងារលុបទំនិញ ---
    if not df.empty:
        st.divider()
        st.subheader("🗑️ លុបទំនិញចេញ")
        product_to_delete = st.selectbox("ជ្រើសរើសទំនិញដែលចង់លុប", df['name'])
        if st.button("បញ្ជាក់ការលុប", type="primary"):
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE name = ?", (product_to_delete,))
            conn.commit()
            conn.close()
            st.warning(f"បានលុប {product_to_delete} រួចរាល់!")
            time.sleep(1)
            st.rerun()