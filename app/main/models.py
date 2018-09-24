from datetime import datetime

from sqlalchemy import (Column, Integer, String, DateTime, UniqueConstraint,
                        ForeignKey, Date)
from sqlalchemy.orm import relationship
from flask_sqlalchemy import Model

from app.extensions import db


def ColumnFK(foreign_key: str, nullable=False):
    return Column(Integer, ForeignKey(foreign_key), nullable=nullable)


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} ({self.id})>'

    def __str__(self):
        return f'<{self.__class__.__name__} ({self.id})>'


class TimeStampedModelMixin(db.Model):
    __abstract__ = True
    # Columns
    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Product(Base):
    __tablename__ = 'products'
    # Columns
    name = Column(String(255), nullable=False, unique=True)
    stock_minimum = Column(Integer, default=1, nullable=False)
    # Relationships
    specifications = relationship('Specification',
                                  cascade='all, delete-orphan',
                                  back_populates='product')


class Specification(Base):
    __tablename__ = 'specifications'
    __table_args__ = (
        UniqueConstraint(
            'product_id', 'manufacturer', 'catalog_number',
            name='unique_specification'),)
    # Columns
    product_id = ColumnFK('products.id')
    manufacturer = Column(String(255), nullable=True)
    catalog_number = Column(String(255), nullable=True)
    units = Column(Integer, default=1, nullable=False)
    # Relationships
    product = relationship('Product',
                           back_populates='specifications')


class Stock(Base):
    __tablename__ = 'stocks'
    # Columns
    name = Column(String(255), nullable=False, unique=True)
    # Relationships
    stock_products = relationship('StockProduct',
                                  cascade='all, delete-orphan',
                                  back_populates='stock')

    @staticmethod
    def insert_main_stock():
        stock = Stock.query.filter_by(name='main').first()
        if not stock:
            stock = Stock(name='main').create()


class StockProduct(Base):
    __tablename__ = 'stock_products'
    __table_args__ = (UniqueConstraint(
        'stock_id', 'product_id', 'lot_number',
        name='unique_stock_product'),)
    # Columns
    stock_id = ColumnFK('stocks.id')
    product_id = ColumnFK('products.id')
    lot_number = Column(String(255), nullable=False)
    expiration_date = Column(Date, nullable=True)
    amount = Column(Integer, default=0, nullable=False)
    # Relationships
    stock = relationship('Stock',
                         back_populates='stock_products')
    product = relationship('Product')
