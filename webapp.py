import streamlit as st
import sqlite3
import pandas as pd
import time
import io
from extra_streamlit_components import CookieManager

st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងអាជីវកម្ម", layout="wide")
cookie_manager = CookieManager()

def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, cost REAL, price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, quantity INTEGER, 
                       cost_price REAL, sale_price REAL, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def login():
    try:
        CORRECT_USER = st.secrets["credentials"]["username"]
        CORRECT_PASS = st.secrets["credentials"]["password"]
    except:
        st.error("សូមកំណត់ Secrets (credentials) ក្នុង Streamlit Cloud!")
        return False
    
    if "logged_in" not in st.session_state: 
        st.session_state["logged_in"] = False
    
    cookie_status = cookie_manager.get(cookie="is_logged_in")
    if cookie_status == "true": 
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ចូលប្រើប្រាស់</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ចូលប្រើ"):
            if u == CORRECT_USER and p == CORRECT_PASS:
                cookie_manager.set("is_logged_in", "true", max_age=86400)
                st.session_state["logged_in"] = True
                st.rerun()
        return False
    return True

# ចាប់ផ្ដើមដំណើរការកម្មវិធីចម្បង
if login():
    with st.sidebar:
        # បង្ហាញឈ្មោះហាងជាមុនសិន (ឱ្យឃើញជានិច្ច)
        st.title("មួយ (១)") 
        
        # បន្ទាប់មកសាកល្បងបង្ហាញរូបភាព បើរកមិនឃើញក៏មិនថ្វី
        try:
            st.image("logo.png", width=100) 
        except:
            st.info("Logo មិនទាន់ត្រូវបានដំឡើង")

        st.divider() # បន្ថែមបន្ទាត់កាត់ដើម្បីឱ្យមើលទៅស្អាត
        
        st.header("📝 គ្រប់គ្រងទិន្នន័យ")
        with st.form("add_product", clear_on_submit=True):
            n_name = st.text_input("ឈ្មោះទំនិញ")
            n_stock = st.number_input("ចំនួនស្តុក", min_value=0)
            n_cost = st.number_input("តម្លៃដើម ($)", min_value=0.0)
            n_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0)
            if st.form_submit_button("បញ្ចូលទំនិញថ្មី"):
                if n_name:
                    with sqlite3.connect('business.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO products (name, stock, cost, price) VALUES (?, ?, ?, ?)", 
                                       (n_name, n_stock, n_cost, n_price))
                        conn.commit()
                    st.rerun()
        
        if st.button("ចាកចេញ (Log out)"):
            cookie_manager.delete("is_logged_in")
            st.session_state["logged_in"] = False
            st.rerun()

    # ទាញទិន្នន័យពី SQLite
    with sqlite3.connect('business.db') as conn:
        df = pd.read_sql_query("SELECT * FROM products", conn)
        sales_df = pd.read_sql_query("SELECT * FROM sales_history ORDER BY sale_time DESC", conn)

    tab_pos, tab_inv, tab_rep = st.tabs(["💰 ផ្នែកលក់ (POS)", "📦 ស្តុកទំនិញ", "📊 របាយការណ៍"])

    with tab_pos:
        st.subheader("លក់ទំនិញចេញ")
        if not df.empty:
            col1, col2 = st.columns(2)
            item = col1.selectbox("រើសទំនិញ", df['name'])
            qty = col2.number_input("ចំនួនលក់", min_value=1, step=1)
            cur = df[df['name'] == item].iloc[0]
            
            if st.button(f"លក់ {item} (សរុប: ${qty*cur['price']:,.2f})"):
                if cur['stock'] >= qty:
                    with sqlite3.connect('business.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (qty, item))
                        cursor.execute("INSERT INTO sales_history (product_name, quantity, cost_price, sale_price, total_price) VALUES (?, ?, ?, ?, ?)", 
                                       (item, qty, cur['cost'], cur['price'], qty*cur['price']))
                        conn.commit()
                    st.success(f"បានលក់ {item} រួចរាល់!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ស្តុកមិនគ្រប់គ្រាន់!")

    with tab_inv:
        search = st.text_input("🔍 ស្វែងរកក្នុងស្តុក...")
        display_df = df[df['name'].str.contains(search, case=False)] if search else df
        st.dataframe(display_df, use_container_width=True)
        
        if not display_df.empty:
            to_del = st.selectbox("លុបទំនិញ", display_df['name'])
            if st.button("បញ្ជាក់ការលុប", type="primary"):
                with sqlite3.connect('business.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM products WHERE name=?", (to_del,))
                    conn.commit()
                st.rerun()

    with tab_rep:
        if not sales_df.empty:
            sales_df['profit'] = (sales_df['sale_price'] - sales_df['cost_price']) * sales_df['quantity']
            total_rev = sales_df['total_price'].sum()
            total_prof = sales_df['profit'].sum()
            c_inv_val = (df['stock'] * df['cost']).sum()

            c1, c2, c3 = st.columns(3)
            c1.metric("ដើមទុនក្នុងស្តុក", f"${c_inv_val:,.2f}")
            c2.metric("ចំណូលសរុប", f"${total_rev:,.2f}")
            c3.metric("ចំណេញសុទ្ធ", f"${total_prof:,.2f}")

            st.divider()
            st.download_button("📥 ទាញយកជា Excel", data=to_excel(sales_df), file_name='report.xlsx')
    
            st.subheader("📈 ក្រាហ្វិកចំណូល")
            daily_rev = sales_df.groupby(pd.to_datetime(sales_df['sale_time']).dt.date)['total_price'].sum()
            st.line_chart(daily_rev)