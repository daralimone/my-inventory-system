from sqlalchemy import create_engine, text # pyright: ignore[reportMissingImports]
import streamlit as st
import pandas as pd
import time
import io
import requests
from extra_streamlit_components import CookieManager
from fpdf import FPDF # pyright: ignore[reportMissingModuleSource]
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")

# --- ១. ការភ្ជាប់ទៅកាន់ SUPABASE (CLOUD DATABASE) ---
# ប្រាកដថាបានដាក់ [database] url ក្នុង Streamlit Secrets រួចរាល់
try:
    db_url = st.secrets["database"]["url"]
    engine = create_engine(db_url)
except Exception as e:
    st.error("សូមពិនិត្យមើលការកំណត់ Secrets (Database URL) ក្នុង Streamlit Cloud!")
    st.stop()

# --- ២. មុខងារជំនួយ (HELPER FUNCTIONS) ---

def send_telegram_msg(message):
    """ផ្ញើសារដំណឹងទៅកាន់ Telegram"""
    token = "8555663996:AAExEgJFLytVVIpg7YYd0UEUkoML7mV38RM" 
    chat_id = "8514197348" 
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

def generate_receipt(item_name, qty, price, total):
    """បង្កើតវិក្កយបត្រជា PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="ONE (1) STORE - RECEIPT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt=f"Item: {item_name}", ln=True)
    pdf.cell(200, 10, txt=f"Quantity: {qty}", ln=True)
    pdf.cell(200, 10, txt=f"Unit Price: ${price:.2f}", ln=True)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, txt=f"Total Amount: ${total:.2f}", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(200, 10, txt="Thank you for shopping with us!", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- ៣. ការរៀបចំ DATABASE (INITIALIZATION) ---

def init_db():
    """បង្កើតតារាងក្នុង Supabase ប្រសិនបើមិនទាន់មាន"""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY, 
                name TEXT UNIQUE, 
                stock INTEGER DEFAULT 0, 
                cost REAL DEFAULT 0.0, 
                price REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS sales_history (
                id SERIAL PRIMARY KEY, 
                product_name TEXT, 
                quantity INTEGER, 
                cost_price REAL, 
                sale_price REAL, 
                total_price REAL, 
                sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY, 
                description TEXT, 
                amount REAL, 
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

# ដំណើរការបង្កើតតារាងភ្លាមៗពេលបើក App
init_db()

# --- ៤. ប្រព័ន្ធសុវត្ថិភាព (AUTHENTICATION) ---

st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងអាជីវកម្ម One (1)", layout="wide")
cookie_manager = CookieManager()

def login():
    if "logged_in" not in st.session_state: 
        st.session_state["logged_in"] = False
    
    # ពិនិត្យ Cookie ដើម្បីឱ្យ Login ជាប់រហូត (Auto-login)
    if cookie_manager.get(cookie="is_logged_in") == "true": 
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ចូលប្រើប្រាស់ប្រព័ន្ធ One (1)</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ចូលប្រើ"):
            if u == st.secrets["credentials"]["username"] and p == st.secrets["credentials"]["password"]:
                cookie_manager.set("is_logged_in", "true", max_age=86400)
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("អត្តសញ្ញាណមិនត្រឹមត្រូវ!")
        return False
    return True

# --- ៥. ផ្នែកសំខាន់នៃកម្មវិធី (MAIN APP) ---

if login():
    # Sidebar - បន្ថែមទំនិញថ្មី
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>🏪 ហាង មួយ (១)</h2>", unsafe_allow_html=True)
        try:
            st.image("logo.png", width=100)
        except:
            st.write("🏪")
        
        st.divider()
        st.subheader("📝 បន្ថែមទំនិញថ្មី")
        with st.form("add_product", clear_on_submit=True):
            n_name = st.text_input("ឈ្មោះទំនិញ")
            n_stock = st.number_input("ចំនួនស្តុក", min_value=0)
            n_cost = st.number_input("តម្លៃដើម ($)", min_value=0.0)
            n_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0)
            if st.form_submit_button("បញ្ចូលទៅក្នុង Supabase"):
                if n_name:
                    try:
                        new_item = pd.DataFrame([{"name": n_name, "stock": n_stock, "cost": n_cost, "price": n_price}])
                        new_item.to_sql('products', engine, if_exists='append', index=False)
                        st.success("បានបញ្ចូលជោគជ័យ!")
                        st.rerun()
                    except:
                        st.error("ឈ្មោះទំនិញនេះមានរួចហើយ!")

        st.divider()
        if st.button("ចាកចេញ (Log out)"):
            cookie_manager.delete("is_logged_in")
            st.session_state["logged_in"] = False
            st.rerun()

    # ទាញទិន្នន័យបច្ចុប្បន្នពី Supabase
    with engine.connect() as conn:
        df_products = pd.read_sql_table("products", conn)
        df_sales = pd.read_sql_table("sales_history", conn)
        df_expenses = pd.read_sql_table("expenses", conn)

    # ការរៀបចំ Tab
    tab_pos, tab_inv, tab_exp, tab_rep = st.tabs(["💰 ផ្នែកលក់ (POS)", "📦 ស្តុក", "💸 ចំណាយ", "📊 របាយការណ៍"])

    # --- Tab 1: ផ្នែកលក់ (POS) ---
    with tab_pos:
        st.subheader("🛒 លក់ទំនិញចេញ")
        if not df_products.empty:
            col1, col2 = st.columns(2)
            selected_item = col1.selectbox("រើសទំនិញ", df_products['name'])
            sale_qty = col2.number_input("ចំនួនលក់", min_value=1, step=1)
            
            product_data = df_products[df_products['name'] == selected_item].iloc[0]
            total_price = sale_qty * product_data['price']
            
            if st.button(f"បញ្ជាក់ការលក់ (សរុប: ${total_price:,.2f})", type="primary"):
                if product_data['stock'] >= sale_qty:
                    with engine.begin() as conn:
                        # កាត់ស្តុក
                        conn.execute(text("UPDATE products SET stock = stock - :q WHERE name = :n"), 
                                     {"q": sale_qty, "n": selected_item})
                        # កត់ត្រាការលក់
                        conn.execute(text("""INSERT INTO sales_history (product_name, quantity, cost_price, sale_price, total_price) 
                                            VALUES (:n, :q, :c, :p, :t)"""), 
                                     {"n": selected_item, "q": sale_qty, "c": product_data['cost'], 
                                      "p": product_data['price'], "t": total_price})
                    
                    send_telegram_msg(f"🛍️ លក់ថ្មី៖ {selected_item} x {sale_qty} | សរុប៖ ${total_price:,.2f}")
                    st.success(f"បានលក់ {selected_item} រួចរាល់!")
                    
                    # ទាញយកវិក្កយបត្រ
                    pdf_file = generate_receipt(selected_item, sale_qty, product_data['price'], total_price)
                    st.download_button(label="📄 ទាញយកវិក្កយបត្រ (PDF)", data=pdf_file, 
                                       file_name=f"receipt_{selected_item}.pdf", mime="application/pdf")
                    st.rerun()
                else:
                    st.error("ស្តុកមិនគ្រប់គ្រាន់ទេ!")

    # --- Tab 2: ស្តុកទំនិញ ---
    with tab_inv:
        st.subheader("📦 បញ្ជីស្តុកបច្ចុប្បន្ន (Cloud)")
        st.dataframe(df_products.style.apply(lambda x: ['background-color: #ffcccc' if x.stock < 5 else '' for _ in x], axis=1), use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ លុបទំនិញ")
        if not df_products.empty:
            item_to_del = st.selectbox("ជ្រើសរើសទំនិញដែលចង់លុប", df_products['name'], key="del")
            if st.button(f"លុប {item_to_del} ចេញជាស្ថាពរ", type="primary"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM products WHERE name = :n"), {"n": item_to_del})
                st.warning(f"បានលុបទំនិញ {item_to_del} រួចរាល់!")
                st.rerun()

    # --- Tab 3: ចំណាយ (Expenses) ---
    with tab_exp:
        st.subheader("💸 កត់ត្រាចំណាយផ្សេងៗ")
        with st.form("expense_form", clear_on_submit=True):
            exp_desc = st.text_input("ពិពណ៌នាចំណាយ")
            exp_amt = st.number_input("ទឹកប្រាក់ ($)", min_value=0.0)
            if st.form_submit_button("រក្សាទុកចំណាយ"):
                if exp_desc and exp_amt > 0:
                    exp_data = pd.DataFrame([{"description": exp_desc, "amount": exp_amt}])
                    exp_data.to_sql('expenses', engine, if_exists='append', index=False)
                    st.success("បានកត់ត្រាចំណាយ!")
                    st.rerun()
        st.dataframe(df_expenses, use_container_width=True)

    # --- Tab 4: របាយការណ៍ (Reports) ---
    with tab_rep:
        st.subheader("📊 សេចក្តីសង្ខេបអាជីវកម្ម")
        c1, c2, c3 = st.columns(3)
        
        total_rev = df_sales['total_price'].sum() if not df_sales.empty else 0
        total_exp = df_expenses['amount'].sum() if not df_expenses.empty else 0
        cogs = (df_sales['cost_price'] * df_sales['quantity']).sum() if not df_sales.empty else 0
        net_profit = total_rev - cogs - total_exp
        
        c1.metric("ចំណូលសរុប", f"${total_rev:,.2f}")
        c2.metric("ចំណាយសរុប (ផ្សេងៗ + ដើម)", f"${(total_exp + cogs):,.2f}")
        c3.metric("ចំណេញសុទ្ធ", f"${net_profit:,.2f}")
        
        if not df_sales.empty:
            st.bar_chart(df_sales.groupby('product_name')['quantity'].sum())
        
        # មុខងារទាញយក Excel
        st.divider()
        st.subheader("📥 ទាញយកទិន្នន័យ (Excel)")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_sales.to_excel(writer, sheet_name='Sales_History', index=False)
            df_expenses.to_excel(writer, sheet_name='Expenses', index=False)
            df_products.to_excel(writer, sheet_name='Current_Stock', index=False)
        
        st.download_button(
            label="📊 ទាញយករបាយការណ៍ទាំងអស់ជា Excel",
            data=buffer.getvalue(),
            file_name=f"report_one_store_{time.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.divider()
        if st.checkbox("🛠️ បង្ហាញមុខងារសម្អាតទិន្នន័យ"):
            if st.button("❌ លុបប្រវត្តិលក់ទាំងអស់"):
                with engine.begin() as conn:
                    conn.execute(text("TRUNCATE TABLE sales_history"))
                st.success("បានសម្អាតប្រវត្តិលក់!")
                st.rerun()