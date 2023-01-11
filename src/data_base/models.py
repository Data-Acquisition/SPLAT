from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Card(Base):
  __tablename__ = 'Cards'
  
  category = Column(String(250), nullable=False)
  count = Column(BigInteger, nullable=False)
  space = Column(String(250), nullable=False) #ozon or wb
  
  __mapper_args__ = {
    "primary_key": [category]
  }
  
class Seller(Base):
  __tablename__ = 'Sellers'
  
  category = Column(String(250), nullable=False)
  count = Column(BigInteger, nullable=False)
  space = Column(String(250), nullable=False)
  
  __mapper_args__ = {
    "primary_key": [category]
  }
  
class Price(Base):
  __tablename__ = 'Prices'
  
  category = Column(String(250), nullable=False)
  name_seller = Column(String(250), nullable=False)
  price = Column(Float, nullable=False)
  space = Column(String(250), nullable=False)
  
  __mapper_args__ = {
    "primary_key": [name_seller]
  }
  
class Rate(Base):
  __tablename__ = 'Rating'
  
  category = Column(String(250), nullable=False)
  name_seller = Column(String(250), nullable=False)
  rate = Column(Float, nullable=False)
  space = Column(String(250), nullable=False) #ozon or wb
  
  __mapper_args__ = {
    "primary_key": [name_seller]
  }
 
class Review(Base):
  __tablename__ = 'Reviews'
  
  category = Column(String(250), nullable=False)
  count = Column(BigInteger, nullable=False)
  space = Column(String(250), nullable=False)
 
  __mapper_args__ = {
    "primary_key": [category]
  }
  
Base.metadata.create_all(engine)
  
  
def add_cards(cat, count):
  card = Card(category=cat, count=count)
  session.add(card)
  session.commit()
  return card
  
def add_seller(cat, count):
  seller = Seller(category=cat, count=count)
  session.add(seller)
  session.commit()
  return seller
  
def add_price(cat, name, price):
  prices = Price(category=cat, name_seller=name, price=price)
  session.add(prices)
  session.commit()
  return prices
  
def add_rate(cat, name, rate):
  rating = Rate(category=cat, name_seller=name, rate=rate)
  session.add(rating)
  session.commit()
  return rating

def add_review(cat, count):
  review = Review(category=cat, count=count)
  session.add(review)
  session.commit()
  return review
