from datbass.models import *
from datbass import session

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