import xml.etree.ElementTree as ET
import sqlite3
import os

def update_xml_to_db(input_file, db_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create table if it doesn't exist
    table_name = 'MCKsale'
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (branch_name TEXT, PriceUpdateDate TEXT, ItemCode TEXT PRIMARY KEY, ItemType TEXT, ItemName TEXT, ManufactureName TEXT, ManufactureCountry TEXT, ManufactureItemDescription TEXT, UnitQty TEXT, Quantity TEXT, UnitMeasure TEXT, BisWeighted TEXT, QtyInPackage TEXT, ItemPrice TEXT, UnitOfMeasurePrice TEXT, AllowDiscount TEXT, itemStatus TEXT, LastUpdateDate TEXT, LastUpdateTime TEXT);"
    c.execute(create_table_query)

    for product in root.findall('Products/Product'):
        item_code = product.find('ItemCode').text
        price_update_date = product.find('PriceUpdateDate').text

        # Check if the item exists in the database
        c.execute(f"SELECT * FROM {table_name} WHERE ItemCode = ?", (item_code,))
        existing_item = c.fetchone()

        if existing_item:
            existing_update_date = existing_item[0]
            if existing_update_date != price_update_date:
                # Update the row if the price update date is different
                update_query = f"UPDATE {table_name} SET PriceUpdateDate = ? WHERE ItemCode = ?"
                c.execute(update_query, (price_update_date, item_code))
        else:
            # Insert new row if the item doesn't exist
            values = [element.text for element in product]
            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(values))})"
            c.execute(insert_query, values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def process_folder(folder_path, db_file):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xml'):
                xml_path = os.path.join(root, file)
                update_xml_to_db(xml_path, db_file)

# Example usage:
process_folder(r'C:\Users\elior\PycharmProjects\priceses\MCK.XML\MCK.SALE', 'priceDB.db')
