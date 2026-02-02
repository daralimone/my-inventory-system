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

    # --- ១. ទាញទិន្នន័យ ---
    conn = sqlite3.connect('business.db')
    df_all = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    # --- ២. ផ្នែកដាស់តឿនស្តុកជិតអស់ (Low Stock Alert) ---
    low_stock_df = df_all[df_all['stock'] <= 5]
    if not low_stock_df.empty:
        st.warning(f"⚠️ មានទំនិញចំនួន {len(low_stock_df)} មុខដែលជិតអស់ពីស្តុក (សល់តិចជាង ៥)!")
        with st.expander("ចុចមើលបញ្ជីទំនិញជិតអស់"):
            st.table(low_stock_df[['name', 'stock']])

    # --- ៣. ផ្នែកស្វែងរកទំនិញ ---
    search_query = st.text_input("🔍 ស្វែងរកទំនិញតាមឈ្មោះ...", "")

    # --- ៤. Sidebar: បញ្ចូលទំនិញថ្មី ---
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

    # --- ៥. បង្ហាញតារាងទិន្នន័យតាមការស្វែងរក ---
    st.subheader("📋 បញ្ជីទំនិញបច្ចុប្បន្ន")
    if search_query:
        display_df = df_all[df_all['name'].str.contains(search_query, case=False)]
    else:
        display_df = df_all
    st.dataframe(display_df, use_container_width=True)

    # --- ៦. មុខងារលុបទំនិញ ---
    if not df_all.empty:
        st.divider()
        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            product_to_delete = st.selectbox("🗑️ ជ្រើសរើសទំនិញដែលចង់លុប", df_all['name'])
        with col_del2:
            st.write(" ") # បង្កើតចន្លោះ
            st.write(" ")
            if st.button("បញ្ជាក់ការលុបទំនិញ", type="primary", use_container_width=True):
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE name = ?", (product_to_delete,))
                conn.commit()
                conn.close()
                st.warning(f"បានលុប {product_to_delete}!")
                time.sleep(1)
                st.rerun()