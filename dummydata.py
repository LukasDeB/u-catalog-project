from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///catalogdb.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user = User(name="First", email="firstemail@email.com", picture="Some picture")
session.add(user)
session.commit()

category1 = Category(name="Sports", user=user)

session.add(category1)
session.commit()

category2 = Category(name="News", user=user)

session.add(category2)
session.commit()

category3 = Category(name="Old News", user=user)

session.add(category3)
session.commit()

category4 = Category(name="Economy", user=user)

session.add(category4)
session.commit()

category5 = Category(name="Comics", user=user)

session.add(category5)
session.commit()

categoryitem1 = CategoryItem(title="Football", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category1, user=user)

session.add(categoryitem1)
session.commit()

categoryitem2 = CategoryItem(title="Soccer", description="Lorem ipsum dolor sit amet,consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category1, user=user)

session.add(categoryitem2)
session.commit()


categoryitem3 = CategoryItem(title="Today", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category2, user=user)

session.add(categoryitem3)
session.commit()

categoryitem4 = CategoryItem(title="Yesterday", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category3, user=user)

session.add(categoryitem4)
session.commit()


categoryitem5 = CategoryItem(title="Coin Values", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category4, user=user)

session.add(categoryitem5)
session.commit()


categoryitem6 = CategoryItem(title="Old Coin Values", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category4, user=user)

session.add(categoryitem6)
session.commit()


categoryitem7 = CategoryItem(title="Stats", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category4, user=user)

session.add(categoryitem7)
session.commit()


categoryitem8 = CategoryItem(title="Batman", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category5, user=user)

session.add(categoryitem8)
session.commit()


categoryitem9 = CategoryItem(title="Catman", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category5, user=user)

session.add(categoryitem9)
session.commit()


categoryitem10 = CategoryItem(title="Dogman", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category5, user=user)

session.add(categoryitem10)
session.commit()


categoryitem11 = CategoryItem(title="Pigman", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris", category=category5, user=user)

session.add(categoryitem11)
session.commit()
