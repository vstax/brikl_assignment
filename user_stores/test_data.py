import datetime

''' Some example data used for testing '''

def _d(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')

images_1 = ("cb6151c9-d657-4576-8b0e-5b79458aa5f7.jpg", "b93b5077-0942-4589-b986-437cc8164d48.jpg", "randompic.jpg")
images_3 = ("notexisting.jpg", "510a96b4-e5bb-11ed-8c79-482ae314fef4.jpg",)
images_6 = ("83/bb/83bb4321-616b-447b-9211-5c3efd7a71ee.jpg",)

test_products = \
           [ # category, name, description, price, availiablity date, quantity, images
            ("Clothes","Pants","",10.25,_d('2023-01-01'),10,images_1),
            ("Clothes","Shirt","Random color",10.25,_d('2023-01-02'),5,()),
            ("Elecronics","Phone 1","Simple phone",100.25,_d('2023-01-03'),20,images_3),
            ("Electronics","Computer","Out of stock",1000.25,_d('2023-03-02'),0,()),
            ("Randoms","Better computer","In stock",1000.25,_d('2023-03-03'),3,()),
            ("Randoms","Special computer","In stock",1000.25,_d('2023-03-04'),5,images_6),
            ("Randoms","Special computer","In stock",1000.25,_d('2023-03-05'),1,()),
            ("Randoms","Crappy computer","---",800.25,_d('2023-03-20'),0,()),
            ("Weird Cat 1","Product?","---",8,_d('2023-03-10'),10,()),
            ("Weird Cat 1","Product 2","---",1.00,_d('2023-04-22'),10,()),
           ]

user_products = {  # user name -> [(product, is_promotional), ..]
                  'Vasya': [
                            (test_products[0], True),
                            (test_products[1], False),
                            (test_products[2], True),
                            (test_products[3], True),
                            ],
                  'Petya': [
                            (test_products[4], True),
                            (test_products[5], True),
                           ],
                  'A Very Cool Guy': [],
                  'Kiril': [
                            (test_products[6], True),
                            (test_products[7], True),
                            (test_products[8], False),
                            (test_products[9], True),
                           ]
                  }

user_catalogs =   {
                   'Vasya': {
                             'Big empty catalog': [],
                             'Something': [test_products[0], test_products[1]],
                             'random things': [test_products[0], test_products[1], test_products[2]],
                             },
                   'Petya': {
                             'weird stuff': [test_products[4], test_products[5]],
                             'test catalog': [test_products[4]],
                            },
                   'Kiril': {
                             'something?': [test_products[7], test_products[8], test_products[9]],
                             'nothing here': [],
                            },
                  }

user_microstores = {
                    'Vasya': {
                              'micro-micro-micro store!': [test_products[0], test_products[1], test_products[2]],
                              'one more store': [test_products[1]],
                             },
                    'Kiril': {
                              'my micro store': [test_products[8], test_products[9]],
                             },
                   }

# Just put all catalogs into single storefront per user for now
user_storefronts = {
                    'Vasya': { 'Storefront #1': list(user_catalogs['Vasya'].keys()) },
                    'Petya': { 'Cool store': list(user_catalogs['Petya'].keys()) },
                    'Kiril': { 'Store 1': list(user_catalogs['Kiril'].keys()) },
                   }
