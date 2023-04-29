from db import Db

connection_params = 'host=127.0.0.1 dbname=test user=test password=test'

db = Db(connection_params)
db.connect()
users_by_id = db.load_users()
# print(users_by_id)
# products_by_id = db.load_all_products()
# print(products_by_id)

users_by_name = {}
for user in users_by_id.values():
    db.load_all_about_user(user)
    users_by_name[user.username] = user

# print(users_by_id)

user = users_by_name['Vasya']
print('\nProducts from a certain MicroStore in clothes category:')
print(user.microstore_selection(1, category_filter=['Clothes']))
print('\nTwo oldest items in a specific Storefront')
print(user.storefront_selection(1, oldest_amount=2))
user2 = users_by_name['Kiril']
print('\n3 newest positions that are in stock in another MicroStore')
print(user2.microstore_selection(3, newest_amount=3, is_in_stock=True))
