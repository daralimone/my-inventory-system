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

    st.title("📦 គ្រប់គ្រងស្តុក និងវិភាគទិន្នន័យ")

    # --- ១. ទាញទិន្នន័យ ---
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    if not df.empty:
        # គណនាតម្លៃសរុបក្នុងស្តុក (ចំនួន x តម្លៃ)
        df['total_value'] = df['stock'] * df['price']
        total_inv_value = df['total_value'].sum()

        # --- ២. បង្ហាញព័ត៌មានសង្ខេប (Metrics) ---
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("ចំនួនមុខទំនិញសរុប", len(df))
        col_m2.metric("ចំនួនស្តុកសរុប", int(df['stock'].sum()))
        col_m3.metric("តម្លៃស្តុកសរុប ($)", f"{total_inv_value:,.2f}")

        st.divider()

        # --- ៣. ក្រាហ្វិកវិភាគ (Charts) ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📊 ចំនួនស្តុកតាមមុខទំនិញ")
            st.bar_chart(data=df, x="name", y="stock")

        with col_chart2:
            st.subheader("💰 តម្លៃស្តុកតាមមុខទំនិញ ($)")
            st.line_chart(data=df, x="name", y="total_value")

    # --- ៤. ផ្នែកស្វែងរក និងតារាង ---
    search_query = st.text_input("🔍 ស្វែងរកទំនិញ...", "")
    if search_query:
        display_df = df[df['name'].str.contains(search_query, case=False)]
    else:
        display_df = df
    
    st.subheader("📋 បញ្ជីទំនិញបច្ចុប្បន្ន")
    st.dataframe(display_df, use_container_width=True)

    # --- ៥. Sidebar: បញ្ចូលទំនិញថ្មី ---
    st.sidebar.header("📝 បញ្ចូលទិន្នន័យ")
    with st.sidebar.form("add_form", clear_on_submit=True):
        name = st.text_input("ឈ្មោះទំនិញ")
        qty = st.number_input("ចំនួន", min_value=0)
        p_price = st.number_input("តម្លៃ ($)", min_value=0.0, format="%.2f")
        if st.form_submit_button("បញ្ចូលទៅក្នុងស្តុក"):
            if name:
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (name, qty, p_price))
                conn.commit()
                conn.close()
                st.rerun()