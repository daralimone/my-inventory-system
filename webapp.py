import streamlit as st
import sqlite3
import pandas as pd
import time
import io
from extra_streamlit_components import CookieManager
from fpdf import FPDF

def generate_receipt(item_name, qty, price, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ONE (1) STORE - RECEIPT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Item: {item_name}", ln=True)
    pdf.cell(200, 10, txt=f"Quantity: {qty}", ln=True)
    pdf.cell(200, 10, txt=f"Unit Price: ${price:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total: ${total:.2f}", ln=True)
    pdf.cell(200, 10, txt="Thank you for shopping with us!", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងអាជីវកម្ម", layout="wide")
cookie_manager = CookieManager()

def init_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    # តារាងផលិតផល (មានស្រាប់)
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock INTEGER, cost REAL, price REAL)''')
    # តារាងប្រវត្តិលក់ (មានស្រាប់)
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, quantity INTEGER, 
                       cost_price REAL, sale_price REAL, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # បន្ថែមតារាងចំណាយថ្មី (ដាក់ចូលត្រង់នេះ)
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, amount REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
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
        # ប្រើ CSS ដើម្បីបង្ខំឱ្យរូបភាព និងអក្សរទាំងអស់ក្នុង Sidebar នៅចំកណ្ដាល
        st.markdown(
            """
            <style>
                [data-testid="stSidebarNav"] {
                    display: none;
                }
                .centered-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
                .centered-container img {
                    border-radius: 10px; /* ធ្វើឱ្យជ្រុងរូបភាពមូលបន្តិចឱ្យស្អាត */
                    margin-bottom: 10px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # ចាប់ផ្ដើមដាក់ Logo និង ឈ្មោះក្នុង Container ដែលយើងបានកំណត់ CSS មិញ
        with st.container():
            st.markdown('<div class="centered-container">', unsafe_allow_html=True)
            
            try:
                # បង្ហាញ Logo
                st.image("logo.png", width=120)
            except:
                st.write("🖼️")
                
            # បង្ហាញឈ្មោះហាង "មួយ (១)"
            st.markdown("<h1 style='font-size: 25px; margin-top: 0;'>មួយ (១)</h1>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        
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
        st.subheader("📦 បញ្ជីទំនិញក្នុងស្តុក")
        search = st.text_input("🔍 ស្វែងរកក្នុងស្តុក...")
        
        # តម្រងស្វែងរក
        display_df = df[df['name'].str.contains(search, case=False)] if search else df
        
        # បង្កើត Function សម្រាប់ដាក់ពណ៌ព្រមាន (បើតិចជាង ៥ ឱ្យចេញពណ៌ក្រហម)
        def highlight_low_stock(row):
            return ['background-color: #ffcccc' if row.stock < 5 else '' for _ in row]

        if not display_df.empty:
            # បង្ហាញតារាងដែលមានការដាក់ពណ៌
            st.dataframe(display_df.style.apply(highlight_low_stock, axis=1), use_container_width=True)
        else:
            st.info("មិនមានទំនិញក្នុងបញ្ជីឡើយ។")

    with tab_rep:
        with tab_rep:
            with sqlite3.connect('business.db') as conn:
                sales_df = pd.read_sql_query("SELECT * FROM sales_history", conn)
                expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
                products_df = pd.read_sql_query("SELECT * FROM products", conn)

            if not sales_df.empty:
                # ១. គណនាចំណូល និងតម្លៃដើមសរុប
                total_rev = sales_df['total_price'].sum()
                total_cost_of_sales = (sales_df['cost_price'] * sales_df['quantity']).sum()
                
                # ២. គណនាចំណាយផ្សេងៗ (ពី Tab ចំណាយ)
                total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
                
                # ៣. គណនាចំណេញសុទ្ធពិតប្រាកដ
                net_profit = total_rev - total_cost_of_sales - total_expenses
                
                # ៤. គណនាដម្លៃទំនិញដែលនៅសល់ក្នុងស្តុក
                inventory_value = (products_df['stock'] * products_df['cost']).sum()

                # បង្ហាញ Metric ជា ៤ ប្រអប់
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ដើមទុនក្នុងស្តុក", f"${inventory_value:,.2f}")
                c2.metric("ចំណូលសរុប", f"${total_rev:,.2f}")
                c3.metric("ចំណាយផ្សេងៗ", f"${total_expenses:,.2f}", delta_color="inverse")
                c4.metric("ចំណេញសុទ្ធពិត", f"${net_profit:,.2f}")

                st.divider()
                # បង្ហាញក្រាហ្វិកប្រៀបធៀប ចំណូល និង ចំណាយ
                st.subheader("📈 ការប្រៀបធៀបចំណូល និង ចំណាយ")
                comparison_data = pd.DataFrame({
                    'ប្រភេទ': ['ចំណូលសរុប', 'ចំណាយសរុប'],
                    'ចំនួនទឹកប្រាក់ ($)': [total_rev, total_expenses + total_cost_of_sales]
                })
                st.bar_chart(comparison_data.set_index('ប្រភេទ'))

    with tab_exp:
        st.subheader("📝 កត់ត្រាចំណាយថ្មី")
        with st.form("expense_form", clear_on_submit=True):
            ex_desc = st.text_input("ពណ៌នាពីការចំណាយ (ឧ៖ ថ្លៃភ្លើង, ថ្លៃជួលតូប...)")
            ex_amount = st.number_input("ចំនួនទឹកប្រាក់ ($)", min_value=0.0, format="%.2f")
            if st.form_submit_button("រក្សាទុកចំណាយ"):
                if ex_desc and ex_amount > 0:
                    with sqlite3.connect('business.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO expenses (description, amount) VALUES (?, ?)", (ex_desc, ex_amount))
                        conn.commit()
                    st.success("បានកត់ត្រាចំណាយរួចរាល់!")
                    st.rerun()
                else:
                    st.warning("សូមបំពេញព័ត៌មានឱ្យបានគ្រប់គ្រាន់!")

        st.divider()
        st.subheader("📜 ប្រវត្តិចំណាយ")
        with sqlite3.connect('business.db') as conn:
            exp_df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
            st.dataframe(exp_df, use_container_width=True)