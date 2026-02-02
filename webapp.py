import streamlit as st
import sqlite3
import pandas as pd
import time
from extra_streamlit_components import CookieManager

# --- ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តុក & លក់", layout="wide")
cookie_manager = CookieManager()

def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    # តុសម្រាប់ស្តុក
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, price REAL)''')
    # តុសម្រាប់ប្រវត្តិលក់
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, quantity INTEGER, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
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
    if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
    cookie_status = cookie_manager.get(cookie="is_logged_in")
    if cookie_status == "true": st.session_state["logged_in"] = True
    if not st.session_state["logged_in"]:
        # ... ផ្ទាំង Login (ដូចមុន) ...
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ចូលប្រើ"):
            if u == CORRECT_USER and p == CORRECT_PASS:
                cookie_manager.set("is_logged_in", "true", max_age=86400)
                st.session_state["logged_in"] = True
                st.rerun()
        return False
    return True

if login():
    st.title("🛒 ប្រព័ន្ធគ្រប់គ្រងស្តុក និងការលក់")

    # --- ១. ទាញទិន្នន័យ ---
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    sales_df = pd.read_sql_query("SELECT * FROM sales_history ORDER BY sale_time DESC", conn)
    conn.close()

    # --- ២. មុខងារលក់ទំនិញ (Sales Form) ---
    st.subheader("💰 លក់ទំនិញ")
    if not df.empty:
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        item_to_sell = col_s1.selectbox("ជ្រើសរើសទំនិញលក់", df['name'])
        qty_to_sell = col_s2.number_input("ចំនួនលក់", min_value=1, step=1)
        
        current_item = df[df['name'] == item_to_sell].iloc[0]
        total_bill = qty_to_sell * current_item['price']
        
        col_s3.write(f"តម្លៃសរុប: **${total_bill:,.2f}**")
        
        if st.button("បញ្ជាក់ការលក់ ✅", use_container_width=True):
            if current_item['stock'] >= qty_to_sell:
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                # កាត់ស្តុកចេញ
                cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (qty_to_sell, item_to_sell))
                # កត់ចូលប្រវត្តិលក់
                cursor.execute("INSERT INTO sales_history (product_name, quantity, total_price) VALUES (?, ?, ?)", 
                               (item_to_sell, qty_to_sell, total_bill))
                conn.commit()
                conn.close()
                st.success(f"លក់ {item_to_sell} ចំនួន {qty_to_sell} រួចរាល់!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("ស្តុកមិនគ្រប់គ្រាន់សម្រាប់លក់ទេ!")

    st.divider()

    # --- ៣. បង្ហាញរបាយការណ៍ ---
    tab1, tab2 = st.tabs(["📋 បញ្ជីស្តុក", "📜 ប្រវត្តិលក់ដូរ"])
    with tab1:
        st.dataframe(df, use_container_width=True)
    with tab2:
        st.write(f"ចំណូលសរុប: **${sales_df['total_price'].sum():,.2f}**")
        st.dataframe(sales_df, use_container_width=True)

    # --- ៤. Sidebar: បញ្ចូលថ្មី ---
    with st.sidebar:
        st.header("📝 បញ្ចូលទំនិញថ្មី")
        # ... កូដបញ្ចូលទំនិញ (ដូចមុន) ...
        if st.sidebar.button("ចាកចេញ (Log out)"):
            cookie_manager.delete("is_logged_in")
            st.session_state["logged_in"] = False
            st.rerun()