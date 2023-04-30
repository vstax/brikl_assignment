-- product categories
CREATE TABLE IF NOT EXISTS product_categories (
    category_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);


-- unique products
CREATE TABLE IF NOT EXISTS products (
    product_id BIGSERIAL PRIMARY KEY,
    category_id BIGINT,  -- references product_categories
    title VARCHAR(255) NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    price NUMERIC(20,4) NOT NULL,
--    create_date TIMESTAMP WITH TIME ZONE DEFAULT now(),  -- removed for now
    available_date TIMESTAMP WITH TIME ZONE,
    quantity BIGINT NOT NULL,
    -- no UNIQUE constraints in the absence of clear requirements, in practice they are likely needed

    CONSTRAINT fk_products_product_categories FOREIGN KEY(category_id) REFERENCES product_categories(category_id)
);

-- We don't do any DB-level filtering now, so no need for index
--CREATE INDEX product_category_id_idx on products(category_id);
--CREATE INDEX product_available_date_idx on products(available_date);
--CREATE INDEX product_quantity_zero_idx on products(quantity) WHERE quantity = 0;


-- photo references for every product. Duplicate photos are not forbidden
CREATE TABLE IF NOT EXISTS product_images (
    image_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT,  -- references products table
    photo_ref VARCHAR(255) NOT NULL,

    CONSTRAINT fk_product_images_products FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE INDEX product_images_product_id_idx ON product_images (product_id);


-- users
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL
);


-- references products in every user's inventory
CREATE TABLE IF NOT EXISTS user_products (
    user_product_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,  -- references users table
    product_id BIGINT,  -- references products table
    is_promotional BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (user_id, product_id),  -- allow products to be only added once

    CONSTRAINT fk_user_products_users FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_user_products_products FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- index on user_id is implied by constraint


-- catalog groups that users create
CREATE TABLE IF NOT EXISTS user_catalogs (
    user_catalog_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,  -- references users table
    name VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE (user_id, name),  -- catalog names shouldn't repeat for the same user. Or should they?

    CONSTRAINT fk_user_catalogs_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- list of products belonging to each catalog
-- catalog_id should be named user_catalog_id for consistency??
CREATE TABLE IF NOT EXISTS user_catalog_products (
    user_catalog_product_id BIGSERIAL PRIMARY KEY,
    catalog_id BIGINT,  -- references user_catalogs table
    user_product_id BIGINT,  -- references user_products table
    UNIQUE (catalog_id, user_product_id),  -- product can only be in the same catalog once

    CONSTRAINT fk_user_catalog_products_user_catalogs FOREIGN KEY (catalog_id)
        REFERENCES user_catalogs(user_catalog_id),
    CONSTRAINT fk_user_catalog_user_products FOREIGN KEY (user_product_id)
        REFERENCES user_products(user_product_id)
);

-- index on catalog_id is implied by constraint
CREATE INDEX user_catalog_products_user_product_id_idx ON user_catalog_products (user_product_id);


-- storefronts that each user has created
CREATE TABLE IF NOT EXISTS user_storefronts (
    storefront_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    user_id BIGINT,  -- references users table
    UNIQUE (user_id, name),  -- Storefronts names per user are unique

    CONSTRAINT fk_user_storefronts_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- index on user_id is implied by constraint


-- product catalogs in a storefront
-- for simplicity sake, all products must belong to some catalog
-- to be in StoreFront now. Empty or special catalog name can be used
-- and handled specially, if ungrouped products are needed
CREATE TABLE IF NOT EXISTS storefront_catalogs (
    storefront_catalog_id BIGSERIAL PRIMARY KEY,
    storefront_id BIGINT,  -- references user_storefronts table
    catalog_id BIGINT,  -- references user_catalogs table
    UNIQUE (storefront_id, catalog_id),

    CONSTRAINT fk_storefront_catalogs_user_storefronts FOREIGN KEY (storefront_id)
        REFERENCES user_storefronts(storefront_id),
    CONSTRAINT fk_storefront_catalogs_user_catalogs FOREIGN KEY (catalog_id)
        REFERENCES user_catalogs(user_catalog_id)
);

-- index on storefront_id is implied by constraint


/*
-- products in storefront (outside of catalogs)
CREATE TABLE IF NOT EXISTS storefront_products (
    storefront_product_id BIGSERIAL PRIMARY KEY,
    storefront_id BIGINT,  -- references user_storefronts table
    user_product_id BIGINT,  -- references user_products table

    CONSTRAINT fk_storefront_products_user_storefronts FOREIGN KEY (storefront_id)
        REFERENCES user_storefronts(storefront_id),
    CONSTRAINT fk_storefront_products_user_products FOREIGN KEY (user_product_id)
        REFERENCES user_products(user_product_id)
);
*/


-- microstores that each user has created
CREATE TABLE IF NOT EXISTS user_microstores (
    microstore_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    user_id BIGINT,  -- references users table
    UNIQUE (user_id, name),  -- microstores per user have unique names

    CONSTRAINT fk_user_microstores_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- index on user_id is implied by constraint


-- products in a microstore (outside of catalogs)
CREATE TABLE IF NOT EXISTS microstore_products (
    microstore_product_id BIGSERIAL PRIMARY KEY,
    microstore_id BIGINT,  -- references user_microstores table
    user_product_id BIGINT,  -- references user_products table
    UNIQUE (microstore_id, user_product_id),  -- only one of the same product per microstore

    CONSTRAINT fk_microstore_products_user_microstores FOREIGN KEY (microstore_id)
        REFERENCES user_microstores(microstore_id),
    CONSTRAINT fk_microstore_products_user_products FOREIGN KEY (user_product_id)
        REFERENCES user_products(user_product_id)
);

-- index on microstore_id is implied by constraint
