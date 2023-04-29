import operator

''' Basic structures for holding the data '''


class Product:
    def __init__(self, product_id, category, title, description, price, available_date, quantity, photos,
                 is_promotional=None):
        self.product_id = product_id
        self.category = category
        self.title = title
        self.description = description
        self.price = price
        self.available_date = available_date
        self.quantity = quantity
        self.photos = photos
        self.is_promotional = is_promotional  # Can be loaded at the later stage

    repr_str = 'Product(id={},category={},title={},desc={},price={},avail={},quantity={},photos={},is_promotional={})'

    def __repr__(self):
        return self.repr_str.format(self.product_id, self.category, self.title, self.description, self.price,
                                    self.available_date, self.quantity, self.photos, self.is_promotional)


class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.all_products = {}  # product id -> Product() mapping
        self.catalogs = {}      # catalog name -> product_id
        self.products_not_in_catalog = {}     # products that are not in catalog
        self.microstores = {}   # MicroStore id -> MicroStore() mapping
        self.storefronts = {}   # Storefront id -> Storefront()

    repr_str = 'User(id={},username={},products={},catalogs={},extra_products={},microstores={},storefronts={})'

    def __repr__(self):
        return self.repr_str.format(self.user_id, self.username, self.all_products, self.catalogs,
                                    self.products_not_in_catalog, self.microstores, self.storefronts)

    @staticmethod
    def _category_filter(product, categories_list):
        if categories_list is not None:
            return product.category in categories_list
        return True  # no filtering if categories_list is empty

    @staticmethod
    def _availability_filter(product, is_in_stock):
        if is_in_stock is None:
            return True
        if is_in_stock:
            return product.quantity > 0
        else:
            return product.quantity == 0

    @staticmethod
    def _top_oldest(products, oldest_amount):
        return sorted(products, key=operator.attrgetter('available_date'))[:oldest_amount]

    @staticmethod
    def _top_newest(products, newest_amount):
        return sorted(products, key=operator.attrgetter('available_date'), reverse=True)[:newest_amount]

    def _apply_filters(self, unfiltered_products, oldest_amount, newest_amount, category_filter, is_in_stock):
        cat_filtered = (product for product in unfiltered_products if self._category_filter(product, category_filter))
        avail_filtered = (product for product in cat_filtered if self._availability_filter(product, is_in_stock))
        if oldest_amount > 0:  # for convenience, we will ignore newest_amount if oldest_amount was passed
            date_filtered = self._top_oldest(avail_filtered, oldest_amount)
        elif newest_amount > 0:
            date_filtered = self._top_newest(avail_filtered, newest_amount)
        else:  # no date filter
            date_filtered = list(avail_filtered)

        # additional filtering, sorting, etc
        return date_filtered

    def microstore_selection(self, store_id, oldest_amount=0, newest_amount=0, category_filter=None, is_in_stock=None):
        # We assume that the caller uses IDs and not string names to identify MicroStore
        if store_id not in self.microstores:
            return []
        microstore = self.microstores[store_id]

        # Just an example, if there are many filters and sorting conditions, can call a mapping to
        # multiple filter functions or other fancy design
        unfiltered_products = (self.all_products[product_id] for product_id in microstore.products)
        return self._apply_filters(unfiltered_products, oldest_amount, newest_amount, category_filter, is_in_stock)


    def storefront_selection(self, store_id, oldest_amount=0, newest_amount=0, category_filter=None, is_in_stock=None):
        # We assume that the caller uses IDs and not string names for Storefront
        if store_id not in self.storefronts:
            return []
        storefront = self.storefronts[store_id]

        # Just an example, if there are many filters and sorting conditions, can call a mapping to
        # multiple filter functions or other fancy design

        # here we will drop catalog -> product mappings, as there are no requirements and this is just an example
        # also same product id can be referenced in multiple catalogs so let's make the list unique
        product_ids = set(product_id for catalog in storefront.catalogs.values()
                                     for product_id in catalog)
        unfiltered_products = (self.all_products[product_id] for product_id in product_ids)
        return self._apply_filters(unfiltered_products, oldest_amount, newest_amount, category_filter, is_in_stock)


class Storefront:
    def __init__(self, storefront_id, name):
        self.storefront_id = storefront_id
        self.name = name
        self.catalogs = {}  # catalog name -> list of product_id mapping

    repr_str = 'Storefront(id={},name={},catalogs={})'

    def __repr__(self):
        return self.repr_str.format(self.storefront_id, self.name, self.catalogs)

    def add_product(self, catalog_name, products):
        self.catalogs[catalog_name] = products


class MicroStore:
    def __init__(self, microstore_id, name, products):
        self.microstore_id = microstore_id
        self.name = name
        self.products = products  # list of product_id

    repr_str = 'MicroStore(id={},name={},products={})'

    def __repr__(self):
        return self.repr_str.format(self.microstore_id, self.name, self.products)

class ItemsLister:
    def __init__(self):
        pass

