import psycopg2

from stores import User, Product, Storefront, MicroStore
import sql_queries

''' Test code to load data into application '''


class Db:
    def __init__(self, connection_params):
        self.connection_params = connection_params

    def connect(self):
        #        self.conn = psycopg2.connect(self.connection_params, cursor_factory=psycopg2.extras.NamedTupleCursor)
        self.conn = psycopg2.connect(self.connection_params)
        self.conn.autocommit = True  # we don't need long transactions

    def load_users(self):
        users = {}
        with self.conn.cursor() as cursor:
            cursor.execute(sql_queries.LOAD_USERS)
            for user_id, username in cursor:
                users[user_id] = User(user_id, username)
        return users

    def load_all_products(self):
        products = {}
        with self.conn.cursor() as cursor:
            cursor.execute(sql_queries.LOAD_PRODUCTS)
            for product_id, category, title, description, price, available_date, quantity, photos in cursor:
                products[product_id] = Product(product_id, category, title, description, price, available_date,
                                               quantity, photos)
        return products

    def load_products_by_user(self, user_id):
        all_products = {}
        catalogs = {}
        products_not_in_catalog = []
        with self.conn.cursor() as cursor:
            cursor.execute(sql_queries.PRODUCTS_BY_USER, (user_id,))
            for product_id, category, title, description, price, available_date, quantity, photos, \
                    is_promotional, catalog_name in cursor:
                product = Product(product_id, category, title, description, price, available_date, quantity, photos,
                                  is_promotional)
                all_products[product_id] = product
                if catalog_name is not None:
                    # Note: same product existing in different catalogs will get two different instances of Product()
                    # this can be addressed by various means
                    catalogs.setdefault(catalog_name, []).append(product_id)
                else:
                    products_not_in_catalog.append(product_id)
        return all_products, catalogs, products_not_in_catalog

    def load_storefronts(self, user_id):
        storefronts = {}
        with self.conn.cursor() as cursor:
            cursor.execute(sql_queries.LOAD_STOREFRONTS, (user_id,))

            for storefront_id, storefront_name, catalog_name, product_ids in cursor:
                # product_ids will be grouped together, but storefront_ids can repeat
                if storefront_id not in storefronts:
                    storefronts[storefront_id] = Storefront(storefront_id, storefront_name)
                storefronts[storefront_id].add_product(catalog_name, product_ids)
        return storefronts

    def load_microstores(self, user_id):
        microstores = {}
        with self.conn.cursor() as cursor:
            cursor.execute(sql_queries.LOAD_MICROSTORES, (user_id,))
            for microstore_id, microstore_name, product_ids in cursor:
                # All products belonging to microstore_id will be grouped together and microstore_id will be unique
                microstores[microstore_id] = MicroStore(microstore_id, microstore_name, product_ids)
        return microstores

    def load_all_about_user(self, user):
        all_products, catalogs, products_not_in_catalog = self.load_products_by_user(user.user_id)
        user.all_products = all_products
        user.catalogs = catalogs
        user.products_not_in_catalog = products_not_in_catalog
        user.storefronts = self.load_storefronts(user.user_id)
        user.microstores = self.load_microstores(user.user_id)
