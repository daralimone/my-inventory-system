import streamlit as st
import sqlite3
import pandas as pd
import time
import io
from extra_streamlit_components import CookieManager

# --- ១. ការកំណត់ទំព័រ ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងអាជីវកម្មឆ្លាតវៃ", layout="wide")
cookie_manager = CookieManager()

def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    # បង្កើតតារាងផលិតផល (មានតម្លៃដើម Cost)
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, cost REAL, price REAL)''')
    # បង្កើតតារាងប្រវត្តិលក់
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, quantity INTEGER, 
                       cost_price REAL, sale_price REAL, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# មុខងារសម្រាប់ទាញយកជា Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- ២. ប្រព័ន្ធ Login ---
def login():
    try:
        CORRECT_USER = st.secrets["credentials"]["username"]
        CORRECT_PASS = st.secrets["credentials"]["password"]
    except:
        st.error("សូមកំណត់ Secrets ក្នុង Streamlit Cloud!")
        return False

    if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
    
    # ឆែក Cookie ដើម្បីកុំឱ្យបាត់ Login ពេល Refresh
    cookie_status = cookie_manager.get(cookie="is_logged_in")
    if cookie_status == "true": st.session_state["logged_in"] = True

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
                else: st.error("លេខកូដមិនត្រឹមត្រូវ!")
        return False
    return True

# --- ៣. ដំណើរការកម្មវិធីចម្បង ---
if login():
    # Sidebar សម្រាប់បញ្ចូលទំនិញ និង Logout
    with st.sidebar:
        st.header("📝 គ្រប់គ្រងទិន្នន័យ")
        with st.form("add_product", clear_on_submit=True):
            n_name = st.text_input("ឈ្មោះទំនិញ")
            n_stock = st.number_input("ចំនួនស្តុក", min_value=0)
            n_cost = st.number_input("តម្លៃដើម ($)", min_value=0.0)
            n_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0)
            if st.form_submit_button("បញ្ចូលទំនិញថ្មី"):
                if n_name:
                    conn = sqlite3.connect('business.db')
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO products (name, stock, cost, price) VALUES (?, ?, ?, ?)", (n_name, n_stock, n_cost, n_price))
                    conn.commit()
                    conn.close()
                    st.rerun()
        
        st.divider()
        if st.button("ចាកចេញ (Log out)", use_container_width=True):
            cookie_manager.delete("is_logged_in")
            st.session_state["logged_in"] = False
            st.rerun()

    # ទាញទិន្នន័យមកប្រើ
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    sales_df = pd.read_sql_query("SELECT * FROM sales_history ORDER BY sale_time DESC", conn)
    conn.close()

    # បង្ហាញ Tabs
    tab_pos, tab_inv, tab_rep = st.tabs(["💰 ផ្នែកលក់ (POS)", "📦 ស្តុកទំនិញ", "📊 របាយការណ៍ & វិភាគ"])

    # --- Tab 1: ផ្នែកលក់ ---
    with tab_pos:
        st.subheader("លក់ទំនិញចេញ")
        if not df.empty:
            col1, col2 = st.columns(2)
            item = col1.selectbox("រើសទំនិញ", df['name'])
            qty = col2.number_input("ចំនួនលក់", min_value=1, step=1)
            
            cur = df[df['name'] == item].iloc[0]
            if st.button(f"លក់ {item} (សរុប: ${qty*cur['price']:,.2f})"):
                if cur['stock'] >= qty:
                    conn = sqlite3.connect('business.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (qty, item))
                    cursor.execute("INSERT INTO sales_history (product_name, quantity, cost_price, sale_price, total_price) VALUES (?, ?, ?, ?, ?)", 
                                   (item, qty, cur['cost'], cur['price'], qty*cur['price']))
                    conn.commit()
                    conn.close()
                    st.success("លក់រួចរាល់!")
                    time.sleep(1)
                    st.rerun()
                else: st.error("ស្តុកមិនគ្រប់គ្រាន់!")

    # --- Tab 2: គ្រប់គ្រងស្តុក ---
    with tab_inv:
        search = st.text_input("🔍 ស្វែងរកក្នុងស្តុក...")
        display_df = df[df['name'].str.contains(search, case=False)] if search else df
        st.dataframe(display_df, use_container_width=True)
        
        # មុខងារលុប
        if not display_df.empty:
            to_del = st.selectbox("លុបទំនិញ", display_df['name'])
            if st.button("បញ្ជាក់ការលុប", type="primary"):
                conn = sqlite3.connect('business.db')
                cursor.execute("DELETE FROM products WHERE name=?", (to_del,))
                conn.commit()
                conn.close()
                st.rerun()

    # --- Tab 3: របាយការណ៍ ---
   with tab_rep:
        if not sales_df.empty:
            # ១. គណនាទិន្នន័យ
            sales_df['profit'] = (sales_df['sale_price'] - sales_df['cost_price']) * sales_df['quantity']
            total_rev = sales_df['total_price'].sum()
            total_prof = sales_df['profit'].sum()
            
            # គណនាដើមទុនក្នុងស្តុកបច្ចុប្បន្ន
            current_inv_value = (df['stock'] * df['cost']).sum()

            # ២. បង្ហាញជាប្រអប់ Metric (Dashboard)
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.metric("ដើមទុនក្នុងស្តុក", f"${current_inv_value:,.2f}")
            col_d2.metric("ចំណូលសរុប", f"${total_rev:,.2f}")
            col_d3.metric("ចំណេញសុទ្ធ", f"${total_prof:,.2f}", delta=f"{(total_prof/total_rev)*100:.1f}%")

            st.divider()
            
            # ៣. ក្រាហ្វិកចំណូលប្រចាំថ្ងៃ
            st.subheader("📈 ក្រាហ្វិកចំណូល")
            daily_rev = sales_df.groupby(pd.to_datetime(sales_df['sale_time']).dt.date)['total_price'].sum()
            st.line_chart(daily_rev)
        if not sales_df.empty:
            sales_df['profit'] = (sales_df['sale_price'] - sales_df['cost_price']) * sales_df['quantity']
            st.metric("ចំណេញសរុប", f"${sales_df['profit'].sum():,.2f}")
            st.line_chart(sales_df.groupby(pd.to_datetime(sales_df['sale_time']).dt.date)['total_price'].sum())
            st.download_button("📥 ទាញយករបាយការណ៍ (Excel)", data=to_excel(sales_df), file_name='report.xlsx')