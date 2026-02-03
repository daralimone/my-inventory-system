import streamlit as st
import pandas as pd
import time
import io
import requests
from sqlalchemy import create_engine, text
from extra_streamlit_components import CookieManager
from fpdf import FPDF

# --- ១. ការរៀបចំការភ្ជាប់ទៅ Supabase ---
# ត្រូវប្រាកដថាបានដាក់ [database] url ក្នុង Streamlit Secrets រួចរាល់
db_url = st.secrets["database"]["url"]
engine = create_engine(db_url)

# --- មុខងារផ្ញើសារ Telegram ---
def send_telegram_msg(message):
    token = "8555663996:AAExEgJFLytVVIpg7YYd0UEUkoML7mV38RM" 
    chat_id = "8514197348" 
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url)
    except:
        pass

# --- មុខងារបង្កើតវិក្កយបត្រ PDF ---
def generate_receipt(item_name, qty, price, total):
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

st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងអាជីវកម្ម One (1)", layout="wide")
cookie_manager = CookieManager()

# --- ២. បង្កើតតារាងក្នុង Supabase (ប្រសិនបើមិនទាន់មាន) ---
def init_db():
    with engine.begin() as conn:
        # តារាងផលិតផល
        conn.execute(text("""CREATE TABLE IF NOT EXISTS products 
                            (id SERIAL PRIMARY KEY, name TEXT UNIQUE, stock INTEGER, cost REAL, price REAL)"""))
        # តារាងប្រវត្តិលក់
        conn.execute(text("""CREATE TABLE IF NOT EXISTS sales_history 
                            (id SERIAL PRIMARY KEY, product_name TEXT, quantity INTEGER, 
                             cost_price REAL, sale_price REAL, total_price REAL, sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""))
        # តារាងចំណាយ
        conn.execute(text("""CREATE TABLE IF NOT EXISTS expenses 
                            (id SERIAL PRIMARY KEY, description TEXT, amount REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""))

init_db()

# --- Login Logic ---
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

if login():
    with st.sidebar:
        st.markdown("<style>.stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }</style>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            try:
                st.image("logo.png", width=120)
            except:
                st.write("🖼️")
            st.markdown("<h1 style='font-size: 25px;'>មួយ (១)</h1>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.header("📝 បន្ថែមទំនិញថ្មី")
        with st.form("add_product", clear_on_submit=True):
            n_name = st.text_input("ឈ្មោះទំនិញ")
            n_stock = st.number_input("ចំនួនស្តុក", min_value=0)
            n_cost = st.number_input("តម្លៃដើម ($)", min_value=0.0)
            n_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0)
            if st.form_submit_button("បញ្ចូលទំនិញ"):
                if n_name:
                    new_item = pd.DataFrame([{"name": n_name, "stock": n_stock, "cost": n_cost, "price": n_price}])
                    new_item.to_sql('products', engine, if_exists='append', index=False)
                    st.success("បានបញ្ចូលទំនិញទៅកាន់ Supabase!")
                    st.rerun()

        if st.button("ចាកចេញ (Log out)"):
            cookie_manager.delete("is_logged_in")
            st.session_state["logged_in"] = False
            st.rerun()

    # --- ៣. ទាញទិន្នន័យពី Supabase ---
    with engine.connect() as conn:
        df = pd.read_sql_table("products", conn)
        sales_df = pd.read_sql_table("sales_history", conn)
        exp_df = pd.read_sql_table("expenses", conn)

    tab_pos, tab_inv, tab_exp, tab_rep = st.tabs(["💰 ផ្នែកលក់ (POS)", "📦 ស្តុកទំនិញ", "💸 ចំណាយ", "📊 របាយការណ៍"])

    with tab_pos:
        st.subheader("🛒 លក់ទំនិញចេញ")
        if not df.empty:
            col1, col2 = st.columns(2)
            item_name = col1.selectbox("រើសទំនិញ", df['name'])
            qty = col2.number_input("ចំនួនលក់", min_value=1, step=1)
            cur = df[df['name'] == item_name].iloc[0]
            total_p = qty * cur['price']
            
            if st.button(f"បញ្ជាក់ការលក់ (សរុប: ${total_p:,.2f})"):
                if cur['stock'] >= qty:
                    with engine.begin() as conn:
                        # កាត់ស្តុក
                        conn.execute(text("UPDATE products SET stock = stock - :q WHERE name = :n"), {"q": qty, "n": item_name})
                        # កត់ត្រាប្រវត្តិលក់
                        conn.execute(text("""INSERT INTO sales_history (product_name, quantity, cost_price, sale_price, total_price) 
                                            VALUES (:n, :q, :c, :p, :t)"""), 
                                     {"n": item_name, "q": qty, "c": cur['cost'], "p": cur['price'], "t": total_p})
                    
                    send_telegram_msg(f"🛍️ លក់ថ្មី៖ {item_name} x {qty} | សរុប៖ ${total_p:,.2f}")
                    st.success(f"បានលក់ {item_name} រួចរាល់!")
                    pdf_data = generate_receipt(item_name, qty, cur['price'], total_p)
                    st.download_button(label="📄 ទាញយកវិក្កយបត្រ (PDF)", data=pdf_data, file_name=f"receipt_{item_name}.pdf", mime="application/pdf")
                    st.rerun()
                else:
                    st.error("ស្តុកមិនគ្រប់គ្រាន់!")

    with tab_inv:
        st.subheader("📦 បញ្ជីស្តុក (Supabase)")
        st.dataframe(df.style.apply(lambda row: ['background-color: #ffcccc' if row.stock < 5 else '' for _ in row], axis=1), use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ លុបទំនិញ")
        if not df.empty:
            del_item = st.selectbox("ជ្រើសរើសទំនិញដែលចង់លុប", df['name'], key="del_box")
            if st.button(f"លុប {del_item} ជាស្ថាពរ", type="primary"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM products WHERE name = :n"), {"n": del_item})
                st.warning("បានលុប!")
                st.rerun()

    with tab_exp:
        st.subheader("💸 កត់ត្រាចំណាយ")
        with st.form("ex_form", clear_on_submit=True):
            d = st.text_input("ពិពណ៌នាចំណាយ")
            a = st.number_input("ទឹកប្រាក់ ($)", min_value=0.0)
            if st.form_submit_button("រក្សាទុក"):
                if d and a > 0:
                    new_exp = pd.DataFrame([{"description": d, "amount": a}])
                    new_exp.to_sql('expenses', engine, if_exists='append', index=False)
                    st.rerun()
        st.dataframe(exp_df, use_container_width=True)

    with tab_rep:
        st.subheader("📊 របាយការណ៍សង្ខេប")
        c1, c2, c3 = st.columns(3)
        rev = sales_df['total_price'].sum() if not sales_df.empty else 0
        exp = exp_df['amount'].sum() if not exp_df.empty else 0
        c1.metric("ចំណូលសរុប", f"${rev:,.2f}")
        c2.metric("ចំណាយសរុប", f"${exp:,.2f}")
        
        cogs = (sales_df['cost_price'] * sales_df['quantity']).sum() if not sales_df.empty else 0
        profit = rev - cogs - exp
        c3.metric("ចំណេញសុទ្ធ", f"${profit:,.2f}")
        
        if not sales_df.empty:
            st.bar_chart(sales_df.groupby('product_name')['quantity'].sum())

        st.divider()
        if st.checkbox("🛠️ បង្ហាញមុខងារសម្អាតទិន្នន័យ"):
            if st.button("❌ លុបប្រវត្តិលក់ទាំងអស់", type="primary"):
                with engine.begin() as conn:
                    conn.execute(text("TRUNCATE TABLE sales_history"))
                st.success("បានសម្អាត!")
                st.rerun()