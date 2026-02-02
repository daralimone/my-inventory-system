import streamlit as st
import sqlite3
import pandas as pd

# --- ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តង់ដា", layout="wide")

# --- ១. មុខងារបង្កើតតារាងចាំបាច់ក្នុង Database ---
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

# --- ២. មុខងារ Login (Username & Password) ---
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
                # លេខកូដសម្ងាត់ថ្មីរបស់អ្នក
                if username == "daralim.one" and password == "aSd.12345678":
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("ឈ្មោះ ឬ លេខកូដមិនត្រឹមត្រូវ!")
        return False
    else:
        if st.sidebar.button("ចាកចេញ (Log out)"):
            st.session_state["logged_in"] = False
            st.rerun()
        return True

# --- ៣. មុខងារទាញទិន្នន័យ ---
def get_data():
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

# --- ៤. ដំណើរការកម្មវិធីចម្បង ---
if login():
    st.title("📦 ប្រព័ន្ធគ្រប់គ្រងស្តុក និងលក់ដូរ")
    
    # --- Sidebar: Form បញ្ចូលគ្រប់យ៉ាងក្នុងប៊ូតុងតែមួយ ---
    st.sidebar.header("📝 គ្រប់គ្រងទិន្នន័យ")
    with st.sidebar.form("my_form", clear_on_submit=True):
        st.write("➕ បញ្ចូលទំនិញថ្មី")
        new_name = st.text_input("ឈ្មោះទំនិញ")
        new_qty = st.number_input("ចំនួនក្នុងស្តុក", min_value=0, step=1)
        new_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("បញ្ចូលទៅក្នុងប្រព័ន្ធ")

        if submitted:
            if new_name:
                conn = sqlite3.connect('business.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", 
                               (new_name, new_qty, new_price))
                conn.commit()
                conn.close()
                st.sidebar.success(f"✅ បានបញ្ចូល {new_name} រួចរាល់!")
                st.rerun()
            else:
                st.sidebar.error("⚠️ សូមបញ្ចូលឈ្មោះទំនិញ!")

    # --- តួសេចក្តីកណ្តាល ---
    df_products = get_data()
    tab1, tab2 = st.tabs(["📊 ស្តុកបច្ចុប្បន្ន", "📈 ស្ថិតិលក់"])

    with tab1:
        st.subheader("📋 បញ្ជីទំនិញ")
        st.dataframe(df_products, use_container_width=True)
        
        st.divider()
        st.subheader("🛒 ការលក់ទំនិញ")
        if not df_products.empty:
            selected_item = st.selectbox("ជ្រើសរើសទំនិញសម្រាប់លក់", df_products['name'])
            qty_to_sell = st.number_input("ចំនួនដែលលក់", min_value=1, step=1)
            
            if st.button("បញ្ជាក់ការលក់"):
                product_info = df_products[df_products['name'] == selected_item].iloc[0]
                current_stock = product_info['stock']
                if current_stock >= qty_to_sell:
                    new_stock = current_stock - qty_to_sell
                    total_p = qty_to_sell * product_info['price']
                    
                    conn = sqlite3.connect('business.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET stock = ? WHERE name = ?", (int(new_stock), selected_item))
                    cursor.execute("INSERT INTO sales_history (product_name, quantity, total_price) VALUES (?, ?, ?)", 
                                   (selected_item, qty_to_sell, total_p))
                    conn.commit()
                    conn.close()
                    st.success(f"លក់ជោគជ័យ! សរុប: {total_p}$")
                    st.rerun()
                else:
                    st.error("ស្តុកមិនគ្រាន់គ្រាន់ទេ!")

    with tab2:
        if not df_products.empty:
            st.subheader("ក្រាហ្វិកស្តុក")
            st.bar_chart(data=df_products, x="name", y="stock")