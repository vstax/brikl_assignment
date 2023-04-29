## Test code
Yes it's possible to do simple script that pulls postgresql docker image and initializes everything but for now just instructions:

```$ psql
postgres=# CREATE USER test WITH PASSWORD 'test';
postgres=# CREATE DATABASE test OWNER test;
$ psql test -U test -f stores_db/schema.sql
CREATE TABLE
CREATE INDEX
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
$ python user_stores/upload_test_data.py
$ python user_stores/retrieve_data_example.py

Products from a certain MicroStore in clothes category:
[Product(id=1,category=Clothes,title=Pants,desc=,price=10.2500,avail=2023-01-01 00:00:00+07:00,quantity=10,photos=['cb6151c9-d657-4576-8b0e-5b79458aa5f7.jpg', 'b93b5077-0942-4589-b986-437cc8164d48.jpg', 'randompic.jpg'],is_promotional=True), Product(id=2,category=Clothes,title=Shirt,desc=Random color,price=10.2500,avail=2023-01-02 00:00:00+07:00,quantity=5,photos=[None],is_promotional=False)]

Two oldest items in a specific Storefront
[Product(id=1,category=Clothes,title=Pants,desc=,price=10.2500,avail=2023-01-01 00:00:00+07:00,quantity=10,photos=['cb6151c9-d657-4576-8b0e-5b79458aa5f7.jpg', 'b93b5077-0942-4589-b986-437cc8164d48.jpg', 'randompic.jpg'],is_promotional=True), Product(id=1,category=Clothes,title=Pants,desc=,price=10.2500,avail=2023-01-01 00:00:00+07:00,quantity=10,photos=['cb6151c9-d657-4576-8b0e-5b79458aa5f7.jpg', 'b93b5077-0942-4589-b986-437cc8164d48.jpg', 'randompic.jpg'],is_promotional=True)]

3 newest positions that are in stock in another MicroStore
[Product(id=10,category=Weird Cat 1,title=Product 2,desc=---,price=1.0000,avail=2023-04-22 00:00:00+07:00,quantity=10,photos=[None],is_promotional=True), Product(id=9,category=Weird Cat 1,title=Product?,desc=---,price=8.0000,avail=2023-03-10 00:00:00+07:00,quantity=10,photos=[None],is_promotional=False)]
```

Running `upload_test_data.py` second time will result in duplicate products for the reasons described below, which is expected. For the rest of data, duplicates are avoided as catalog names and store names have to be unique per user (which is also not in the requirements, but makes sense here). Data used for testing is stored in Python as well since working with CSV on tables normalized in such way is not easy.

Testing upload / data retrieval code is out of scope of the requirements and is for demonstration purposes only (yes it's very messy). Some aspects like referencing Storefronts and Microstores by ID instead of name are just to make code less complicated.


## Product implementation details
* Prices are stored as fixed-point numbers with 2 numbers past the fixed point (cents etc), in absence of other requirements. In database we store up to 4 numbers past fixed point to avoid uncontrolled rounding in the stored data; rounding should be done elsewhere.

* Whether empty string or NULL values are allowed is decided according to common sense, in the absence of other requirement and existing code.

* `Create_date` is not in original requirements (now removed)

* This schema assumes product_id as an internal ID generated inside database, it's returned to application. Products with duplicate attributes (except for ID) are allowed, in the absence of other requirements, as currently products don't have any attirbute which can be used to identify them in a unique way.

* Products are not linked to users, so e.g. different users can have exactly the same product in store at least at the DB level. Existing test loader creates different products for different users, obviously. Current schema does not restrict users in manipulating any product on a DB level, in absence of other requirements. At the same time, `product_id` enumeration is global, for simplicity sake. In practice, if products are never shared, `user_id+per_user_product_id` combination should used as a reference, or if `product_id` needs to be global, it shouldn't be exposed to the user. Foundation for that is in place, with catalog/Storefront/MicroStore tables referencing specific `user_product_id` and not `product_id`

* Promotional products are listed as separate entities with is_promotional=TRUE flag set. They don't reference base product or its photos, as that would make design much more complicated and is outside the current requirements. Promitional attribute is stored at user->products mapping level, however if the same product can only be used by one user, it might make sense to move it to "products" table instead.

## Product images
* Photos are stored externally in something like filesystem / object storage / CDN and we keep a string reference to file name or object name in the DB

* Multiple photos per product are supported and are treated as equals, there is no concept of photos priority or main product photo, as that was not in the requirements. In practice, order is likely desired and can be done by adding another column with photos number
* Strict consistency in the DB by the means of foreign key to product table will cause problem when removing a product, as references to photos will be lost without removing photos themselves. Possible solutions include a trigger on deletion from photos table, which populates some kind of "photos to delete" table with obsolete `photo_ref` strings, which is that asynchroniously processed to delete actual photos. Another solution is never deleting products, having some kind of "enabled" flag for them, and ignoring them if the product is disabled. However, some mean of deletion of unused / bad photos is probably still needed. How to organize proper removal of any data is beyond the scope of this assignment.

### Relations
* catalog -> product is a one way mapping, allowing user to put products in multiple catalogs, but that makes product unaware of catalog it's associated with

* `category_id`, `image_id`, `user_catalog_id`, `user_catalog_product_id`, `storefront_catalog_id`, `storefront_product_id`, `microstore_product_id` are only used for keeping relations in the DB in normalized tables and not exposed to the application as they doesn't seem to be useful.

* `product_id`, `user_id`, `storefront_id`, `microstore_id` are exposed to application level to allow easy access and manipulation by ID as opposed to name that can be changed.

* To simplify the view when product is referenced multiple times, User() catalogs / Storefronts / MicroStores only refer to the list of `product_id`, with actual link to Product() and complete data being available in `User.all_products` mapping. They can be replaced with actual references or usage of wrappers that pulls the reference.

* Storefronts and MicroStores: the requirements are somewhat vague and only mention catalogs for Storefronts. I've made an implementation where Storefront only has products belonging to some catalog (though it's allowed to have empty catalog and handle it in a special way), and Microstores keep the list of products directly, without any reference to the catalog.

## General implementation notes
* Code here uses models to load all the data about all products / microstores / storefronts belonging to a user into memory. This is done for demonstration and data manipulation purposes (also, it's probably a good idea for any resonable-sized list of products). Other designs like lazy loading (e.g. getting list of storefronts or microstores first, and then loading product list for each only when it's accessed) are possible, but not required until working with really huge amounts of data. However, keeping all the products and references to them in memory makes usage of indexes in the DB and SQL queries with filters somewhat useless - as strictly speaking, there is no valid reason to access the database for the data that already exists in memory. In real implementation, the code either won't load everything to memory, or the code that loads everything and the code that loads data from DB as per user filters are separated. Since there is not enough information about where it makes sense to filter, all products related to certain user are loaded from the DB and filtering is done in the application.

* DB indexes are probably a bit of an overkill. They are mostly just for show, as with data amount that small they don't matter. Still, all data retrieval according to the current model is more or less optimal.

* Type checking (minimal) is done on the DB side only, application relies on passing types from the DB.

* ORM is not used to demonstrate clean way to design data schemes in the DB and to keep everything explicit.

* Loading from DB (and especially uploading test data to DB) code is for test purposes only and is only for demonstration of data being stored and passing both ways. It is not formatted / cleaned up / designed properly. In actual implementation, server-side functions can be used for efficiently uploading data in a single application->DB interaction, e.g. uploading new product simultaneously with adding category of the product, reflecting user's ownership of the product etc. Current upload is just a quick-and-dirty hack to get some data into the DB.

