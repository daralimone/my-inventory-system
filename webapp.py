import streamlit as st
import sqlite3
import pandas as pd
import time

# --- ១. ការកំណត់ទំព័រ (ត្រូវតែនៅខាងលើគេបង្អស់) ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តង់ដា", layout="wide")

# --- ២. បង្កើតនិយមន័យមុខងារជាមុន (Define first) ---
def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, quantity INTEGER, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# --- ៣. បន្ទាប់មកទើបហៅវាមកប្រើ (Call second) ---
init_db() 

# --- ៤. មុខងារ Login ---
def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ការចូលប្រើប្រាស់ប្រព័ន្ធ</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)")
            password = st.text_input("លេខកូដសម្ងាត់ (Password)", type="password")
            if st.button("ចូលប្រើ", use_container_width=True):
                if username == "daralim.one" and password == "aSd.12345678":
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("ឈ្មោះ ឬ លេខកូដមិនត្រឹមត្រូវ!")
        return False
    return True

# --- ៥. ដំណើរការកម្មវិធីចម្បង ---
if login():
    if st.sidebar.button("ចាកចេញ (Log out)"):
        st.session_state["logged_in"] = False
        st.rerun()

    st.title("📦 ប្រព័ន្ធគ្រប់គ្រងស្តុក និងលក់ដូរ")
    
    # មុខងារទាញទិន្នន័យ
    def get_data():
        conn = sqlite3.connect('business.db')
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        return df

    df_products = get_data()

    # Sidebar Form
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
            st.rerun()

    # តារាងបង្ហាញទំនិញ
    st.subheader("📋 បញ្ជីទំនិញបច្ចុប្បន្ន")
    st.dataframe(df_products, use_container_width=True) 