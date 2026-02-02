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

    st.title("📦 ប្រព័ន្ធគ្រប់គ្រងស្តុកវៃឆ្លាត")

    # --- ១. ទាញទិន្នន័យ ---
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    # --- ២. ផ្នែកកែប្រែទិន្នន័យ (Update Section) ---
    with st.expander("🔄 កែប្រែចំនួនស្តុក ឬ តម្លៃទំនិញ"):
        if not df.empty:
            selected_item = st.selectbox("ជ្រើសរើសទំនិញដើម្បីកែប្រែ", df['name'])
            item_info = df[df['name'] == selected_item].iloc[0]
            
            col_u1, col_u2 = st.columns(2)
            new_stock = col_u1.number_input("ចំនួនស្តុកថ្មី", value=int(item_info['stock']))
            new_price = col_u2.number_input("តម្លៃថ្មី ($)", value=float(item_info['price']), format="%.2f")
            
            if st.button("រក្សាទុកការកែប្រែ", type="secondary"):
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET stock = ?, price = ? WHERE name = ?", 
                               (new_stock, new_price, selected_item))
                conn.commit()
                conn.close()
                st.success(f"បានធ្វើបច្ចុប្បន្នភាព {selected_item} រួចរាល់!")
                time.sleep(1)
                st.rerun()

    st.divider()

    # --- ៣. ការបង្ហាញក្រាហ្វិក និងតារាង (ដូចមុន) ---
    if not df.empty:
        df['total_value'] = df['stock'] * df['price']
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("មុខទំនិញសរុប", len(df))
        col_m2.metric("ស្តុកសរុប", int(df['stock'].sum()))
        col_m3.metric("តម្លៃស្តុកសរុប ($)", f"{df['total_value'].sum():,.2f}")
        
        st.bar_chart(data=df, x="name", y="stock")
        st.dataframe(df[['name', 'stock', 'price', 'total_value']], use_container_width=True)

    # --- ៤. Sidebar: បញ្ចូលថ្មី ---
    st.sidebar.header("📝 បញ្ចូលទំនិញថ្មី")
    with st.sidebar.form("add_form", clear_on_submit=True):
        name = st.text_input("ឈ្មោះទំនិញ")
        qty = st.number_input("ចំនួន", min_value=0)
        p_price = st.number_input("តម្លៃ ($)", min_value=0.0, format="%.2f")
        if st.form_submit_button("បញ្ចូល"):
            if name:
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (name, qty, p_price))
                conn.commit()
                conn.close()
                st.rerun()