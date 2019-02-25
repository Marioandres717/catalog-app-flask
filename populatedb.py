from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, User, Category, Item

engine = create_engine('sqlite:///store.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create User
User1 = User(name="pepito", email="pepito@gmail.com",
             picture="https://www.realmadrid.com/img/horizontal_940px/_1rm4230_hor_20190113073257.jpg")
session.add(User1)
session.commit()

# Category for ManShoes
category1 = Category(name="Man Shoes", description="All kinds of man shoes",
                     picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/kalkopq2mrwmpnggicxi/air-max-90-shoe-7BTDp40j.jpg")

session.add(category1)
session.commit()

# Items for ManShoes category
item1 = Item(name="Nike Air max", description="Supper confortable shoes",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/kalkopq2mrwmpnggicxi/air-max-90-shoe-7BTDp40j.jpg", category=category1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Nike Air jordan", description="Supper confortable shoes",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/kalkopq2mrwmpnggicxi/air-max-90-shoe-7BTDp40j.jpg", category=category1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Nike SBs", description="Supper confortable shoes",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/kalkopq2mrwmpnggicxi/air-max-90-shoe-7BTDp40j.jpg", category=category1, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Nike Air force 1", description="Supper confortable shoes",
             picture="https://c.static-nike.com/a/images/t_PDP_1280_v1/f_auto/kalkopq2mrwmpnggicxi/air-max-90-shoe-7BTDp40j.jpg", category=category1, user_id=1)
session.add(item4)
session.commit()

# Category for ManShoes
category2 = Category(name="Bed sheets", description="The fluffies bed sheets",
                     picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSZdp3-OwchpQ1fkdQ_b6jlF5ikn6LAFNnTM1wSwoQUhLNBL7jKg")

session.add(category2)
session.commit()

# Items for BedSheets category
item1 = Item(name="king size bed sheet", description="Supper confortable shoes",
             picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSZdp3-OwchpQ1fkdQ_b6jlF5ikn6LAFNnTM1wSwoQUhLNBL7jKg", category=category2, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Nike Air jordan", description="Supper confortable shoes",
             picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSZdp3-OwchpQ1fkdQ_b6jlF5ikn6LAFNnTM1wSwoQUhLNBL7jKg", category=category2, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Nike SBs", description="Supper confortable shoes",
             picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSZdp3-OwchpQ1fkdQ_b6jlF5ikn6LAFNnTM1wSwoQUhLNBL7jKg", category=category2, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Nike Air force 1", description="Supper confortable shoes",
             picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSZdp3-OwchpQ1fkdQ_b6jlF5ikn6LAFNnTM1wSwoQUhLNBL7jKg", category=category2, user_id=1)
session.add(item4)
session.commit()
