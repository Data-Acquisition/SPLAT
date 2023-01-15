from datbass.models import *
from datbass import session

def add_cards(cat, count, space, date):
  exist_card = session.query(Card).filter(Card.category == cat)\
    .filter(Card.space == space).first()
  if not exist_card:
    card = Card(category=cat, count=count, space=space, created_at=date) #space - ozon, wb
    session.add(card)
    session.commit()
    return card
  elif exist_card.created_at != date:
    exist_card.count = count
    session.commit()
  
def add_seller(cat, count, space, date):
  exist_seller = session.query(Seller).filter(Seller.category == cat)\
    .filter(Seller.space == space).first()
  if not exist_seller:
    seller = Seller(category=cat, count=count, space=space, created_at=date)
    session.add(seller)
    session.commit()
    return seller
  elif exist_seller.created_at != date:
    exist_seller.count = count
    session.commit()
  
def add_price(id, cat, name, price, space, date):
  exist_price = session.query(Price).filter(Price.id == id).filter(Price.space == space).first()
  if not exist_price:
    prices = Price(id=id, category=cat, name_seller=name, price=price, space=space, created_at=date)
    session.add(prices)
    session.commit()
    return prices
  elif exist_price.created_at != date:
    exist_price.price = price
    session.commit()
  
def add_rate(cat, name, rate, space, date):
  exist_rate = session.query(Rate).filter(Rate.category == cat)\
    .filter(Rate.name_seller == name).filter(Rate.space == space).first()
  if not exist_rate:
    rating = Rate(category=cat, name_seller=name, rate=rate, space=space, created_at=date)
    session.add(rating)
    session.commit()
    return rating
  elif exist_rate.created_at != date:
    exist_rate.rate = rate
    session.commit()

def add_review(cat, count, space, date):
  exist_rev = session.query(Review).filter(Review.category == cat)\
    .filter(Review.space == space).first()
  if not exist_rev:
    review = Review(category=cat, count=count, space=space, created_at=date)
    session.add(review)
    session.commit()
    return review
  elif exist_rev.created_at != date:
    exist_rev.count = count
    session.commit()