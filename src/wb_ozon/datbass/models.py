from datetime import date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, DateTime
from . import engine

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# engine = create_engine('postgresql+psycopg2://localhost:5432/postgres')
# Session = sessionmaker(bind=engine)
# session = Session()

Base = declarative_base()


class Card(Base):
    __tablename__ = 'Cards'

    category = Column(String(250), nullable=False)
    count = Column(BigInteger, nullable=False)
    space = Column(String(250), nullable=False)  # ozon or wb
    created_at = Column(DateTime)

    __mapper_args__ = {
        "primary_key": [category]
    }


class Seller(Base):
    __tablename__ = 'Sellers'

    category = Column(String(250), nullable=False)
    count = Column(BigInteger, nullable=False)
    space = Column(String(250), nullable=False)
    created_at = Column(DateTime)

    __mapper_args__ = {
        "primary_key": [category]
    }


class Price(Base):
    __tablename__ = 'Prices'

    id = Column(BigInteger, nullable=False)
    category = Column(String(250), nullable=False)
    name_seller = Column(String(250), nullable=False)
    price = Column(Float, nullable=False)
    space = Column(String(250), nullable=False)
    created_at = Column(DateTime)
    
    __mapper_args__ = {
        "primary_key": [id]
    }


class Rate(Base):
    __tablename__ = 'Rating'

    category = Column(String(250), nullable=False)
    name_seller = Column(String(250), nullable=False)
    rate = Column(Float, nullable=False)
    space = Column(String(250), nullable=False)  # ozon or wb
    created_at = Column(DateTime)

    __mapper_args__ = {
        "primary_key": [name_seller]
    }


class Review(Base):
    __tablename__ = 'Reviews'

    category = Column(String(250), nullable=False)
    count = Column(BigInteger, nullable=False)
    space = Column(String(250), nullable=False)
    created_at = Column(DateTime)

    __mapper_args__ = {
        "primary_key": [category]
    }


Base.metadata.create_all(engine)
