import sqlite3

def update_product_info(p_id, new_qty, new_price):
    # ១. តភ្ជាប់ទៅ Database
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()

    # ២. សរសេរកូដ SQL ដើម្បីកែទាំង ចំនួនស្តុក និង តម្លៃ ក្នុងពេលតែមួយ
    # SET stock = ? (កែចំនួន)
    # SET price = ? (កែតម្លៃ)
    # WHERE id = ? (កែតែទំនិញណាដែលមានលេខ ID ត្រូវគ្នា)
    sql_script = """
        UPDATE products 
        SET stock = ?, 
            price = ? 
        WHERE id = ?
    """
    
    # បញ្ជូនទិន្នន័យថ្មីចូលទៅតាមលំដាប់លំដោយនៃសញ្ញា ?
    cursor.execute(sql_script, (new_qty, new_price, p_id))

    # ៣. រក្សាទុក (Save)
    conn.commit()
    conn.close()
    print(f"✅ រួចរាល់! ទំនិញលេខ ID {p_id} ត្រូវបានកែប្រែចំនួនទៅ {new_qty} និងតម្លៃទៅ ${new_price}")

# --- របៀបប្រើ ---
# ឧបមាថា ចង់កែទំនិញលេខ ១ (ទឹកក្រូច) ឱ្យសល់ ៨០ ដប និងតម្លៃឡើងដល់ $០.៧
update_product_info(1, 80, 0.7)