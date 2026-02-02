import streamlit as st
import sqlite3
import pandas as pd
import time
from extra_streamlit_components import CookieManager

# --- ១. ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តង់ដា", layout="wide")

# បង្កើត Cookie Manager
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
    # ពិនិត្យ Session State ជាមុនសិន ដើម្បីឱ្យវាលឿន
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # បើកអាន Cookie
    cookie_status = cookie_manager.get(cookie="is_logged_in")
    
    # បើមាន Cookie ស្រាប់ ឱ្យវា Login តែម្ដង
    if cookie_status == "true":
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ការចូលប្រើប្រាស់ប្រព័ន្ធ</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)")
            password = st.text_input("លេខកូដសម្ងាត់ (Password)", type="password")
            
            if st.button("ចូលប្រើ", use_container_width=True):
                if username == "daralim.one" and password == "aSd.12345678":
                    # បង្កើត Cookie និង Set State
                    cookie_manager.set("is_logged_in", "true", max_age=86400)
                    st.session_state["logged_in"] = True
                    st.success("ចូលប្រើជោគជ័យ! កំពុងរៀបចំទំព័រ...")
                    time.sleep(1) # ទុកពេលឱ្យ Cookie ដំណើរការ
                    st.rerun()
                else:
                    st.error("ឈ្មោះ ឬ លេខកូដមិនត្រឹមត្រូវ!")
        return False
    return True

# --- ២. ដំណើរការកម្មវិធីចម្បង ---
if login():
    # ប៊ូតុង Log out
    if st.sidebar.button("ចាកចេញ (Log out)"):
        cookie_manager.delete("is_logged_in")
        st.session_state["logged_in"] = False
        st.rerun()

    st.title("📦 ប្រព័ន្ធគ្រប់គ្រងស្តុក និងលក់ដូរ")
    
    # ដាក់កូដ " get_data() " និង " Sidebar Form " របស់អ្នកនៅទីនេះ...
    st.write("ស្វាគមន៍! ឥឡូវនេះអ្នកអាចប្រើប្រាស់កម្មវិធីបានហើយ។")
    
    # សាកល្បងបង្ហាញតារាងទិន្នន័យ
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    st.dataframe(df, use_container_width=True)
    conn.close() 