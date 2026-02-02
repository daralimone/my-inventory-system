import sqlite3

def delete_product(p_id):
    # ១. តភ្ជាប់ទៅ Database
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()

    # ២. សរសេរកូដ SQL ដើម្បីលុបទំនិញតាមលេខ ID
    # វានឹងលុបជួរដេក (Row) ទាំងមូលនៃទំនិញនោះ
    sql_script = "DELETE FROM products WHERE id = ?"
    
    cursor.execute(sql_script, (p_id,))

    # ៣. រក្សាទុកការផ្លាស់ប្តូរ
    conn.commit()
    conn.close()
    print(f"🗑️ រួចរាល់! ទំនិញដែលមានលេខ ID {p_id} ត្រូវបានលុបចេញពីប្រព័ន្ធ។")

# --- របៀបប្រើ ---
# សាកល្បងលុបទំនិញដែលមាន ID លេខ ២ (ឧទាហរណ៍៖ នំបុ័ង)
delete_product(2)