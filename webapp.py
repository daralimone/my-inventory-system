import streamlit as st
import pandas as pd
import time
import io
import requests
from sqlalchemy import create_engine, text
from extra_streamlit_components import CookieManager
from fpdf import FPDF

# --- ១. ការរៀបចំទំព័រ (ត្រូវតែនៅខាងលើគេបង្អស់) ---
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងអាជីវកម្ម One (1)", layout="wide")
cookie_manager = CookieManager()

# --- ២. ការភ្ជាប់ទៅកាន់ SUPABASE ---
try:
    db_url = st.secrets["database"]["url"]
    engine = create_engine(db_url)
except Exception as e:
    st.error("សូមកំណត់ Database URL ក្នុង Secrets ឱ្យបានត្រឹមត្រូវ!")
    st.stop()

# --- ៣. មុខងារជំនួយ (HELPER FUNCTIONS) ---

def send_telegram_msg(message):
    token = "8555663996:AAExEgJFLytVVIpg7YYd0UEUkoML7mV38RM" 
    chat_id = "8514197348" 
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

def generate_receipt(item_name, qty, price, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 20)
    pdf.cell(190, 15, txt="ONE (1) STORE", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(100, 10, txt=f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.cell(90, 10, txt=f"Receipt No: {int(time.time())}", ln=True, align='R')
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(100, 10, "Description", border=1)
    pdf.cell(30, 10, "Qty", border=1, align='C')
    pdf.cell(60, 10, "Total", border=1, align='C', ln=True)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(100, 10, f"{item_name}", border=1)
    pdf.cell(30, 10, f"{qty}", border=1, align='C')
    pdf.cell(60, 10, f"${total:.2f}", border=1, align='C', ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(190, 10, txt=f"GRAND TOTAL: ${total:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

@st.cache_data(ttl=60) # បញ្ជាឱ្យ App ចងចាំទិន្នន័យរយៈពេល ៦០ វិនាទី ដើម្បីបង្កើនល្បឿន
def get_data():
    with engine.connect() as conn:
        df_p = pd.read_sql_table("products", conn)
        df_s = pd.read_sql_table("sales_history", conn)
        df_e = pd.read_sql_table("expenses", conn)
    return df_p, df_s, df_e

# --- ៤. ប្រព័ន្ធសុវត្ថិភាព (LOGIN) ---

def login():
    if "logged_in" not in st.session_state: 
        st.session_state["logged_in"] = False
    
    if cookie_manager.get(cookie="is_logged_in") == "true":
        st.session_state["logged_in"] = True

    if not st.session_state["logged_in"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ចូលប្រើប្រាស់ One (1)</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ចូលប្រើ"):
            if u == st.secrets["credentials"]["username"] and p == st.secrets["credentials"]["password"]:
                cookie_manager.set("is_logged_in", "true", max_age=86400)
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Username ឬ Password មិនត្រឹមត្រូវ!")
        return False
    return True

# --- ៥. ដំណើរការកម្មវិធី ---

if login():
    # ទាញទិន្នន័យ (ហៅប្រើ function ដែលមាន cache)
    df_products, df_sales, df_expenses = get_data()

    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>🏪 ហាង មួយ (១)</h2>", unsafe_allow_html=True)
        st.divider()
        st.subheader("📝 បន្ថែមទំនិញថ្មី")
        with st.form("add_product", clear_on_submit=True):
            n_name = st.text_input("ឈ្មោះទំនិញ")
            n_stock = st.number_input("ចំនួនស្តុក", min_value=0)
            n_cost = st.number_input("តម្លៃដើម ($)", min_value=0.0)
            n_price = st.number_input("តម្លៃលក់ ($)", min_value=0.0)
            if st.form_submit_button("បញ្ចូលទំនិញ"):
                if n_name:
                    try:
                        new_item = pd.DataFrame([{"name": n_name, "stock": n_stock, "cost": n_cost, "price": n_price}])
                        new_item.to_sql('products', engine, if_exists='append', index=False)
                        st.cache_data.clear() # សម្អាត Cache ដើម្បីឱ្យបង្ហាញទិន្នន័យថ្មីភ្លាមៗ
                        st.success("បានបញ្ចូលជោគជ័យ!")
                        st.rerun()
                    except:
                        st.error("ឈ្មោះទំនិញនេះមានរួចហើយ!")

        if st.button("ចាកចេញ (Log out)"):
            cookie_manager.delete("is_logged_in")
            st.session_state["logged_in"] = False
            st.rerun()

    tab_pos, tab_inv, tab_exp, tab_rep = st.tabs(["💰 ផ្នែកលក់", "📦 ស្តុក", "💸 ចំណាយ", "📊 របាយការណ៍"])

    with tab_pos:
        st.subheader("🛒 លក់ទំនិញ")
        if not df_products.empty:
            col1, col2 = st.columns(2)
            selected_item = col1.selectbox("រើសទំនិញ", df_products['name'])
            sale_qty = col2.number_input("ចំនួនលក់", min_value=1, step=1)
            
            product_data = df_products[df_products['name'] == selected_item].iloc[0]
            total_price = sale_qty * product_data['price']
            
            if st.button(f"លក់ចេញ (សរុប: ${total_price:,.2f})", type="primary"):
                if product_data['stock'] >= sale_qty:
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE products SET stock = stock - :q WHERE name = :n"), {"q": sale_qty, "n": selected_item})
                        conn.execute(text("""INSERT INTO sales_history (product_name, quantity, cost_price, sale_price, total_price) 
                                            VALUES (:n, :q, :c, :p, :t)"""), 
                                    {"n": selected_item, "q": sale_qty, "c": product_data['cost'], "p": product_data['price'], "t": total_price})
                    
                    send_telegram_msg(f"🛍️ លក់៖ {selected_item} x {sale_qty} | សរុប៖ ${total_price:,.2f}")
                    st.cache_data.clear() # សម្អាត Cache ក្រោយពេលលក់រួច
                    st.success("លក់ជោគជ័យ!")
                    pdf_data = generate_receipt(selected_item, sale_qty, product_data['price'], total_price)
                    st.download_button(label="📄 វិក្កយបត្រ (PDF)", data=pdf_data, file_name=f"receipt_{selected_item}.pdf", mime="application/pdf")
                    st.rerun()

    with tab_inv:
        st.subheader("📦 បញ្ជីស្តុក")
        st.dataframe(df_products, use_container_width=True)
        if not df_products.empty:
            item_to_del = st.selectbox("លុបទំនិញ", df_products['name'], key="del_box")
            if st.button("លុបចោល"):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM products WHERE name = :n"), {"n": item_to_del})
                st.cache_data.clear()
                st.rerun()

    with tab_exp:
        st.subheader("💸 ចំណាយ")
        with st.form("exp_form", clear_on_submit=True):
            d = st.text_input("ពិពណ៌នា")
            a = st.number_input("ទឹកប្រាក់ ($)", min_value=0.0)
            if st.form_submit_button("រក្សាទុក"):
                if d and a > 0:
                    pd.DataFrame([{"description": d, "amount": a}]).to_sql('expenses', engine, if_exists='append', index=False)
                    st.cache_data.clear()
                    st.rerun()
        st.dataframe(df_expenses, use_container_width=True)

    with tab_rep:
        st.subheader("📊 របាយការណ៍")
        rev = df_sales['total_price'].sum() if not df_sales.empty else 0
        exp = df_expenses['amount'].sum() if not df_expenses.empty else 0
        cogs = (df_sales['cost_price'] * df_sales['quantity']).sum() if not df_sales.empty else 0
        st.metric("ចំណេញសុទ្ធ", f"${(rev - cogs - exp):,.2f}")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_sales.to_excel(writer, sheet_name='Sales', index=False)
            df_products.to_excel(writer, sheet_name='Stock', index=False)
        st.download_button(label="📊 ទាញយក Excel", data=buffer.getvalue(), file_name="report.xlsx")