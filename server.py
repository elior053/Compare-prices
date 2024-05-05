from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


# SQLite database connection
def get_db_cursor():
    db_conn = sqlite3.connect('priceDB.db')  # Updated the database name
    db_cursor = db_conn.cursor()
    return db_conn, db_cursor


@app.route('/')
def homepage():
    return render_template('homepage.html')  # Load homepage.html template


@app.route('/get_town_suggestions', methods=['GET'])
def get_town_suggestions():
    term = request.args.get('term', '')
    print(f"Received term: {term}")  # Logging
    db_conn, db_cursor = get_db_cursor()
    db_cursor.execute("SELECT english_text FROM city_names WHERE english_text LIKE ? OR hebrew_text LIKE ?",
                      ('%' + term + '%', '%' + term + '%'))
    matching_towns = [row[0] for row in db_cursor.fetchall()]
    db_conn.close()
    print(f"Matching towns: {matching_towns}")  # Logging
    return jsonify(matching_towns)


@app.route('/get_stores_in_town', methods=['GET'])
def get_stores_in_town():
    selected_town = request.args.get('town', '')
    print(f"Selected town: {selected_town}")  # Logging
    db_conn, db_cursor = get_db_cursor()
    db_cursor.execute("SELECT * FROM Branches WHERE adress LIKE ? OR adress LIKE ?", ('%' + selected_town.strip() + '%',
                                                                                      '%אונליין%'))
    store_data = db_cursor.fetchall()

    store_names = [f"{row[2]} | {row[3]}" for row in store_data]  # need to fetch row 2 for printing it

    db_conn.close()
    print(f"Store names for the town: {store_names}")  # Logging
    return jsonify(store_names)


@app.route('/get_product_suggestions', methods=['GET'])
def get_product_suggestions():
    term = request.args.get('term', '')  # Get the search term from the request
    selected_store = request.args.get('store', '')  # Get the selected store name from the request

    if "מחסני השוק" in selected_store:
        store_name = "MCKreg"
    elif "ויקטורי" in selected_store:
        store_name = "VICTORYreg"
    elif "שופרסל" in selected_store:
        store_name = "Shufreg"

    # Fetch product details for AutoComplete suggestions
    db_conn, db_cursor = get_db_cursor()
    query = f"SELECT ItemName, UnitQty, ItemPrice FROM {store_name} JOIN Branches ON {store_name}.branch_id = Branches.branch_id " \
            f"WHERE {store_name}.ItemName LIKE ? COLLATE NOCASE"
    db_cursor.execute(query, ('%' + term + '%',))
    product_details = db_cursor.fetchall()

    # Construct a list of dictionaries with product details
    products = [{'value': row[0], 'label': row[0], 'unitQty': row[1], 'itemPrice': row[2]} for row in product_details]

    db_conn.close()

    return jsonify(products)


@app.route('/get_products_in_other_branches', methods=['GET'])
def get_products_in_other_branches():
    selected_store = request.args.get('store', '')  # Get the selected store name from the request

    # Fetch the city of the selected store
    db_conn, db_cursor = get_db_cursor()
    db_cursor.execute("SELECT town FROM Branches WHERE branch_id = ?", (selected_store,))
    selected_city = db_cursor.fetchone()
    db_conn.close()

    if selected_city is not None:
        selected_city = selected_city[0]  # Extract the city name

        # Fetch all branches in the same city
        db_conn, db_cursor = get_db_cursor()
        db_cursor.execute("SELECT branch_id, town FROM Branches WHERE town = ?", (selected_city,))
        other_branches = db_cursor.fetchall()

        # Initialize a list to store product data from other branches
        products_from_other_branches = []

        # Fetch product details from other branches in the same city
        for branch_id, town in other_branches:
            store_name = ""  # Define a logic to map branch_id to store_name
            query = f"SELECT ItemName, UnitQty, ItemPrice FROM {store_name} JOIN Branches ON {store_name}.branch_id = Branches.branch_id " \
                    f"WHERE Branches.town = ?"
            db_cursor.execute(query, (town,))
            product_details = db_cursor.fetchall()

            # Construct a list of dictionaries with product details
            products = [{'value': row[0], 'label': row[0], 'unitQty': row[1], 'itemPrice': row[2]} for row in product_details]
            products_from_other_branches.append({'branch_id': branch_id, 'town': town, 'products': products})

        db_conn.close()
        return jsonify(products_from_other_branches)
    else:
        return jsonify([])  # Return an empty list if the selected store city is not found



if __name__ == '__main__':
    app.run(debug=True)
