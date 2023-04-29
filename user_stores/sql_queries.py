''' To save time, just keep queries in python instead of DB functions for now '''

LOAD_USERS = 'SELECT user_id, username FROM users'

LOAD_PRODUCTS = '''
SELECT product_id, product_categories.name AS category, title, description, price, available_date,
   quantity, ARRAY_AGG(photo_ref) AS photos
FROM products
JOIN product_categories USING (category_id)
LEFT JOIN product_images USING (product_id)
GROUP BY product_id, category
'''

PRODUCTS_BY_USER = '''
WITH catalogs AS (SELECT name AS catalog_name, user_catalog_id AS catalog_id FROM user_catalogs)
SELECT product_id, product_categories.name AS category, title, description, price, available_date,
       quantity, ARRAY_AGG(photo_ref) as photos, is_promotional, catalog_name
FROM products
JOIN product_categories USING (category_id)
LEFT JOIN product_images USING (product_id)
JOIN user_products USING (product_id)
LEFT JOIN user_catalog_products USING (user_product_id)
LEFT JOIN catalogs USING (catalog_id)
WHERE user_id = %s
GROUP BY product_id, name, is_promotional, catalog_name
'''

LOAD_STOREFRONTS = '''
WITH catalogs AS (SELECT name AS catalog_name, user_catalog_id AS catalog_id FROM user_catalogs)
SELECT storefront_id, name AS storefront_name, catalog_name, ARRAY_AGG(product_id) AS products
FROM user_storefronts
JOIN storefront_catalogs USING (storefront_id)
JOIN user_catalog_products USING (catalog_id)
JOIN user_products USING (user_product_id)
JOIN products USING (product_id)
JOIN catalogs USING (catalog_id)
WHERE user_storefronts.user_id = %s AND is_promotional = TRUE
GROUP BY storefront_id, catalog_name
'''

LOAD_MICROSTORES = '''
SELECT microstore_id, name AS microstore_name, ARRAY_AGG(product_id) AS products
FROM user_microstores
JOIN microstore_products USING (microstore_id)
JOIN user_products USING (user_product_id)
WHERE user_microstores.user_id = %s
GROUP BY microstore_id
'''
