import xml.etree.ElementTree as ET
import sqlite3
import os

def update_promos_to_db(input_file, db_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create table if it doesn't exist
    table_name = 'MCKreg1'
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (PriceUpdateDate TEXT, ItemCode TEXT PRIMARY KEY, ItemType TEXT, IsGiftItem TEXT, RewardType TEXT, AllowMultipleDiscounts TEXT, PromotionID TEXT, PromotionDescription TEXT, PromotionStartDate TEXT, PromotionStartHour TEXT, PromotionEndDate TEXT, PromotionEndHour TEXT, ClubID TEXT, MinQty TEXT, MaxQty TEXT, DiscountRate TEXT, DiscountType TEXT, MinPurchaseAmount TEXT, DiscountedPrice TEXT, DiscountedPricePerMida TEXT, MinNoOfItemsOffered TEXT, AdditionalsCoupon TEXT, AdditionalsGiftCount TEXT, AdditionalsTotals TEXT, AdditionalsMinBasketAmount TEXT, AdditionalRestrictions TEXT, Remarks TEXT);"
    c.execute(create_table_query)

    for sale in root.findall('Sales/Sale'):
        item_code = sale.find('ItemCode').text
        price_update_date = sale.find('PriceUpdateDate').text

        # Check if the promo exists in the database
        c.execute(f"SELECT * FROM {table_name} WHERE ItemCode = ?", (item_code,))
        existing_promo = c.fetchone()

        if existing_promo:
            existing_update_date = existing_promo[0]
            if existing_update_date != price_update_date:
                # Update the row if the price update date is different
                update_query = f"UPDATE {table_name} SET PriceUpdateDate = ? WHERE ItemCode = ?"
                c.execute(update_query, (price_update_date, item_code))
        else:
            # Insert new row if the promo doesn't exist
            values = [element.text for element in sale]
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
                update_promos_to_db(xml_path, db_file)

# Example usage:
process_folder(r'priceses\MCK.XML\MCK.REG', 'priceDB.db')
