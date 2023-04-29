import psycopg2
from test_data import test_products, user_products, user_catalogs, user_microstores, user_storefronts

''' Very basic code to fill DB with some data for testing '''

connection_params = 'host=127.0.0.1 dbname=test user=test password=test'

connection_params = connection_params
conn = psycopg2.connect(connection_params)

with conn.cursor() as cursor:
    # insert users
    cursor.execute('INSERT INTO users (username) SELECT UNNEST(%s) ON CONFLICT DO NOTHING',
                   (list(user_products.keys()),))
    cursor.execute('SELECT username, user_id FROM users')
    username_to_id = dict(cursor)
    # insert products
    cursor.execute('INSERT INTO product_categories (name) SELECT UNNEST(%s) ON CONFLICT DO NOTHING',
                   (list(set(c[0] for c in test_products)),))
    conn.commit()

    cursor.execute('SELECT name, category_id FROM product_categories')
    category_to_id = dict(cursor)
    product_to_id = {}  # extremly weird mapping since we don't want to bother using real Product() here
    for product in test_products:
        cursor.execute('INSERT INTO products (category_id, title, description, price, available_date, quantity) '
                       'VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id', (category_to_id[product[0]], product[1],
                                                                                product[2], product[3], product[4],
                                                                                product[5]))
        product_id = cursor.fetchone()[0]
        product_to_id[product] = product_id
        for product_image in product[6]:
            cursor.execute('INSERT INTO product_images (product_id, photo_ref) VALUES (%s, %s)',
                           (product_id, product_image))
    conn.commit()

    product_to_user_product_id = {}  # Another hack to simplify testing, since product is associated with one user
    for username, products in user_products.items():
        for product, is_promotional in products:
            cursor.execute('INSERT INTO user_products (user_id, product_id, is_promotional) VALUES (%s, %s, %s)'
                           'RETURNING user_product_id',
                           (username_to_id[username], product_to_id[product], is_promotional))
            product_to_user_product_id[product] = cursor.fetchone()[0]
    conn.commit()

    for username, catalogs in user_catalogs.items():
        for catalog_name, products in catalogs.items():
            cursor.execute('INSERT INTO user_catalogs (user_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                           (username_to_id[username], catalog_name))
        cursor.execute('SELECT name, user_catalog_id FROM user_catalogs')
        catalog_name_to_id = dict(cursor)
        for catalog_name, products in catalogs.items():
            for product in products:
                cursor.execute('INSERT INTO user_catalog_products (catalog_id, user_product_id) VALUES (%s, %s)',
                               (catalog_name_to_id[catalog_name], product_to_user_product_id[product]))
    conn.commit()

    for username, microstores in user_microstores.items():
        for microstore_name, products in microstores.items():
            cursor.execute('INSERT INTO user_microstores (user_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                           (username_to_id[username], microstore_name))
        cursor.execute('SELECT name, microstore_id FROM user_microstores')
        microstore_name_to_id = dict(cursor)
        for microstore_name, products in microstores.items():
            for product in products:
                cursor.execute('INSERT INTO microstore_products (microstore_id, user_product_id) VALUES (%s, %s)',
                               (microstore_name_to_id[microstore_name], product_to_user_product_id[product]))
    conn.commit()

    for username, microstores in user_microstores.items():
        for microstore_name, products in microstores.items():
            cursor.execute('INSERT INTO user_microstores (user_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                           (username_to_id[username], microstore_name))
        cursor.execute('SELECT name, microstore_id FROM user_microstores')
        microstore_name_to_id = dict(cursor)
        for microstore_name, products in microstores.items():
            for product in products:
                cursor.execute('INSERT INTO microstore_products (microstore_id, user_product_id) VALUES (%s, %s)'
                               'ON CONFLICT DO NOTHING',
                               (microstore_name_to_id[microstore_name], product_to_user_product_id[product]))
    conn.commit()

    for username, storefronts in user_storefronts.items():
        for storefront_name, products in storefronts.items():
            cursor.execute('INSERT INTO user_storefronts (user_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                           (username_to_id[username], storefront_name))
        cursor.execute('SELECT name, storefront_id FROM user_storefronts')
        storefront_name_to_id = dict(cursor)
        for storefront_name, catalog_names in storefronts.items():
            for catalog_name in catalog_names:
                cursor.execute('INSERT INTO storefront_catalogs (storefront_id, catalog_id) VALUES (%s, %s)'
                               'ON CONFLICT DO NOTHING',
                               (storefront_name_to_id[storefront_name], catalog_name_to_id[catalog_name]))
    conn.commit()


conn.close()
