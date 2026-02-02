import streamlit as st
import sqlite3
import pandas as pd
import time
from extra_streamlit_components import CookieManager

# --- ១. ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តុក", layout="wide")

# បង្កើត Cookie Manager សម្រាប់ចងចាំការចូលប្រើ
cookie_manager = CookieManager()

def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, quantity INTEGER, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def login():
    # ទាញយក Username និង Password ពី Secrets ដែលអ្នកបាន Save មិញ
    try:
        CORRECT_USER = st.secrets["credentials"]["username"]
        CORRECT_PASS = st.secrets["credentials"]["password"]
    except:
        st.error("សូមកំណត់ Username និង Password ក្នុងផ្នែក Secrets ជាមុនសិន!")
        return False

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # ពិនិត្យមើល Cookie ដើម្បីកុំឱ្យវាយលេខកូដពេល Refresh
    cookie_status = cookie_manager.get(cookie="is_logged_in")
    if cookie_status == "true":
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ចូលប្រើប្រាស់ប្រព័ន្ធ</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់")
            password = st.text_input("លេខកូដសម្ងាត់", type="password")
            if st.button("ចូលប្រើ", use_container_width=True):
                if username == CORRECT_USER and password == CORRECT_PASS:
                    cookie_manager.set("is_logged_in", "true", max_age=86400) # ចងចាំ ១ ថ្ងៃ
                    st.session_state["logged_in"] = True
                    st.success("ជោគជ័យ!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ឈ្មោះ ឬ លេខកូដមិនត្រឹមត្រូវ!")
        return False
    return True

# --- ២. ដំណើរការកម្មវិធីចម្បង ---
if login():
    # ប៊ូតុង Log out (លុប Cookie ចោល)
    if st.sidebar.button("ចាកចេញ (Log out)"):
        cookie_manager.delete("is_logged_in")
        st.session_state["logged_in"] = False
        st.rerun()

    st.title("📦 គ្រប់គ្រងស្តុក និងលក់ដូរ")
    
    # --- Sidebar: បញ្ចូលទំនិញថ្មី ---
    st.sidebar.header("📝 បញ្ចូលទិន្នន័យ")
    with st.sidebar.form("add_form", clear_on_submit=True):
        name = st.text_input("ឈ្មោះទំនិញ")
        qty = st.number_input("ចំនួន", min_value=0, step=1)
        price = st.number_input("តម្លៃ ($)", min_value=0.0, format="%.2f")
        if st.form_submit_button("បញ្ចូលទៅក្នុងស្តុក"):
            if name:
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (name, qty, price))
                conn.commit()
                conn.close()
                st.sidebar.success(f"បានបញ្ចូល {name}!")
                st.rerun()

    # --- បង្ហាញតារាងទិន្នន័យ ---
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    st.subheader("📋 បញ្ជីទំនិញក្នុងស្តុក")
    st.dataframe(df, use_container_width=True)
    conn.close()