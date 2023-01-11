from datbass.models import *
from datbass import session

def add_cards(cat, count, space):
  card = Card(category=cat, count=count, space=space) #space - ozon, wb
  session.add(card)
  session.commit()
  return card
  
def add_seller(cat, count, space):
  seller = Seller(category=cat, count=count, space=space)
  session.add(seller)
  session.commit()
  return seller
  
def add_price(cat, name, price, space):
  prices = Price(category=cat, name_seller=name, price=price, space=space)
  session.add(prices)
  session.commit()
  return prices
  
def add_rate(cat, name, rate, space):
  rating = Rate(category=cat, name_seller=name, rate=rate, space=space)
  session.add(rating)
  session.commit()
  return rating

def add_review(cat, count, space):
  review = Review(category=cat, count=count, space=space)
  session.add(review)
  session.commit()
  return review