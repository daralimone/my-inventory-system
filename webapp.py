import streamlit as st
import sqlite3
import pandas as pd
import time
from extra_streamlit_components import CookieManager

# --- ១. ការកំណត់ទំព័រ (ត្រូវនៅខាងលើគេបង្អស់) ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តង់ដា", layout="wide")

# បង្កើត Cookie Manager សម្រាប់ចងចាំការចូលប្រើ
cookie_manager = CookieManager()

# --- ២. បង្កើតនិយមន័យមុខងារ Database ---
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

# --- ៣. មុខងារ Login ដោយប្រើ Cookie ---
def login():
    # ទាញយក Cookie "is_logged_in" ពី Browser
    is_logged_in = cookie_manager.get(cookie="is_logged_in")

    # បើគ្មាន Cookie ទេ បង្ហាញផ្ទាំង Login
    if is_logged_in != "true":
        st.markdown("<h2 style='text-align: center;'>🔐 ការចូលប្រើប្រាស់ប្រព័ន្ធ</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)")
            password = st.text_input("លេខកូដសម្ងាត់ (Password)", type="password")
            
            if st.button("ចូលប្រើ", use_container_width=True):
                if username == "daralim.one" and password == "aSd.12345678":
                    # រក្សាទុក Cookie រយៈពេល ១ ថ្ងៃ (៨៦៤០០ វិនាទី)
                    cookie_manager.set("is_logged_in", "true", max_age=86400)
                    st.success("ចូលប្រើជោគជ័យ!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ឈ្មោះ ឬ លេខកូដមិនត្រឹមត្រូវ!")
        return False
    return True

# --- ៤. ដំណើរការកម្មវិធីចម្បង ---
if login():
    # ប៊ូតុង Log out (លុប Cookie ចោល)
    if st.sidebar.button("ចាកចេញ (Log out)"):
        cookie_manager.delete("is_logged_in")
        st.rerun()

    st.title("📦 ប្រព័ន្ធគ្រប់គ្រងស្តុក និងលក់ដូរ")
    
    # មុខងារទាញទិន្នន័យ
    def get_data():
        conn = sqlite3.connect('business.db')
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        return df

    df_products = get_data()

    # Sidebar Form សម្រាប់បញ្ចូលទំនិញ
    st.sidebar.header("📝 គ្រប់គ្រងទិន្នន័យ")
    with st.sidebar.form("my_form", clear_on_submit=True):
        st.write("➕ បញ្ចូលទំនិញថ្មី")
        new_name = st.text_input("ឈ្មោះទំនិញ")
        new_qty = st.number_input("ចំនួនក្នុងស្តុក", min_value=0, step=1)
        new_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("បញ្ចូលទៅក្នុងប្រព័ន្ធ")

        if submitted and new_name:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (new_name, new_qty, new_price))
            conn.commit()
            conn.close()
            st.sidebar.success(f"✅ បានបញ្ចូល {new_name} រួចរាល់!")
            time.sleep(1)
            st.rerun()

    # តារាងបង្ហាញទំនិញ
    st.subheader("📋 បញ្ជីទំនិញបច្ចុប្បន្ន")
    st.dataframe(df_products, use_container_width=True) 