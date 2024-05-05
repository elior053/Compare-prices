import xml.etree.ElementTree as ET
import sqlite3
import os

def update_promotions_to_db(input_file, db_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create table if it doesn't exist
    table_name = 'ShufSALE'
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (PromotionId TEXT PRIMARY KEY, AllowMultipleDiscounts TEXT, PromotionDescription TEXT, PromotionUpdateDate TEXT, PromotionStartDate TEXT, PromotionStartHour TEXT, PromotionEndDate TEXT, PromotionEndHour TEXT, IsWeightedPromo TEXT, MinQty TEXT, DiscountType TEXT, RewardType TEXT, DiscountRate TEXT, MinNoOfItemOfered TEXT, ItemCode TEXT, ItemType TEXT, IsGiftItem TEXT, AdditionalIsCoupon TEXT, AdditionalGiftCount TEXT, AdditionalIsTotal TEXT, AdditionalIsActive TEXT, ClubId TEXT);"
    c.execute(create_table_query)

    for promotion in root.findall('Promotions/Promotion'):
        promotion_id = promotion.find('PromotionId').text
        promotion_update_date = promotion.find('PromotionUpdateDate').text
        item = promotion.find('PromotionItems/Item')

        # Check if the promotion exists in the database
        c.execute(f"SELECT * FROM {table_name} WHERE PromotionId = ?", (promotion_id,))
        existing_promotion = c.fetchone()

        if existing_promotion:
            existing_update_date = existing_promotion[3]
            if existing_update_date != promotion_update_date:
                # Update the row if the promotion update date is different
                update_query = f"UPDATE {table_name} SET PromotionUpdateDate = ? WHERE PromotionId = ?"
                c.execute(update_query, (promotion_update_date, promotion_id))
        else:
            # Insert new row if the promotion doesn't exist
            values = [element.text for element in promotion]
            if item is not None:
                values.extend([item.find('ItemCode').text, item.find('ItemType').text, item.find('IsGiftItem').text])
            else:
                values.extend(['', '', ''])  # Fill empty values for missing item data
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
                update_promotions_to_db(xml_path, db_file)

# Example usage:
process_folder(r'C:\Users\elior\PycharmProjects\priceses\Shufersal.xml\SHUFsale', 'priceDB.db')
