from app import db
from app.models import User, Category, Item

# Create User
User = User(name="pepito", email="pepito@gmail.com",
             picture="https://www.realmadrid.com/img/horizontal_940px/_1rm4230_hor_20190113073257.jpg")  # noqa
db.session.add(User)
db.session.commit()

# Category for ManShoes
category1 = Category(name="Man Shoes", description="All kinds of man shoes",
                     picture="https://nssdata.s3.amazonaws.com/images/galleries/10546/adidas-yeezy.jpg")  # noqa

db.session.add(category1)
db.session.commit()


# Items for ManShoes category
item1 = Item(name="Nike Air Max", description="Supper confortable shoes",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/kalkopq2mrwmpnggicxi/air-max-90-shoe-7BTDp40j.jpg", category=category1, seller=User)  # noqa
db.session.add(item1)
db.session.commit()

item2 = Item(name="Nike Air Jordan", description="Ball Shoes",
             picture="https://n1.sdlcdn.com/imgs/h/y/n/Nike-Air-Jordan-32-Red-SDL064811552-1-80960.jpeg", category=category1, seller=User)  # noqa
db.session.add(item2)
db.session.commit()

item3 = Item(name="Nike SBs", description="Skater Shoes",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/eckhkyh6s1jaliaxysqb/sb-solarsoft-portmore-2-skate-shoe-XPTblOOk.jpg", category=category1, seller=User)  # noqa
db.session.add(item3)
db.session.commit()

item4 = Item(name="Nike Air Force 1", description="Classic Shoes",
             picture="https://www.flightclub.com/media/catalog/product/cache/1/image/1600x1140/9df78eab33525d08d6e5fb8d27136e95/8/0/804342_01.jpg", category=category1, seller=User)  # noqa
db.session.add(item4)
db.session.commit()

# Category for hoodies
category2 = Category(name="Hoodies", description="Stylist hoodies",
                     picture="https://images.unsplash.com/photo-1501078319173-5d5298f2faf8?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=701&q=80")  # noqa

db.session.add(category2)
db.session.commit()

# Items for BedSheets category
item1 = Item(name="Pullover Cotton Hoodie", description="Nike black hoodie",  # noqa
             picture="https://i.ebayimg.com/images/g/NewAAOSwFJBZQALj/s-l1600.jpg", category=category2, seller=User)  # noqa
db.session.add(item1)
db.session.commit()

item2 = Item(name="Classic Fleece Hoodie", description="Nike grey hoodie",
             picture="https://i.pinimg.com/originals/90/15/8a/90158af2b3533e6c5d0a1e829d31234c.jpg", category=category2, seller=User)  # noqa
db.session.add(item2)
db.session.commit()

item3 = Item(name="Wizards Therma Hoodie", description="Nike Washington Wizard hoodie",  # noqa
             picture="https://cdnc.lystit.com/1200/630/tr/photos/nike/0daec29e/nike-University-RedBlackWhite-Washington-Wizards-Therma-Flex-Showtime-Mens-Nba-Hoodie.jpeg", category=category2, seller=User)  # noqa
db.session.add(item3)
db.session.commit()

item4 = Item(name="Serrated Trefoil Hoodie", description="Adidas Originals Man",  # noqa
             picture="https://getthelabel.btxmedia.com/pws/client/images/catalogue/products/ah9742/xlarge/ah9742_black.jpg", category=category2, seller=User)  # noqa
db.session.add(item4)
db.session.commit()

# Category for T-shirts
category3 = Category(name="T-shirts", description="Unique T-shirt",
                     picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/whn7dx0nck8aogggl8by/sb-logo-t-shirt-jnTp8rym.jpg")  # noqa
db.session.add(category3)
db.session.commit()

item1 = Item(name="Nike Older Kid", description="Black kids T-shirt",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/qvj9ofdedooz6ocibjbt/air-older-t-shirt-2KTrDOp7.jpg", category=category3, seller=User)  # noqa
db.session.add(item1)
db.session.commit()

item2 = Item(name="Nike Dry White", description="Just do it",
             picture="https://cdn2.basket4ballers.com/72365-large_default/t-shirt-nike-dry-white-924260-100.jpg", category=category3, seller=User)  # noqa
db.session.add(item2)
db.session.commit()

item3 = Item(name="BYU Nike", description="Ball T-shirt",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/jzy7ystiwhryw18d0izs/fff-dri-fit-t-shirt-AKTdNRJw.jpg", category=category3, seller=User)  # noqa
db.session.add(item3)
db.session.commit()
