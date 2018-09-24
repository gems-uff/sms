from datetime import datetime

from sqlalchemy import (Column, Integer, String, DateTime, UniqueConstraint,
                        ForeignKey, Date, Numeric, Boolean, CheckConstraint)
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import Model

from app.extensions import db


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
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    manufacturer = Column(String(255), nullable=True)
    catalog_number = Column(String(255), nullable=True)
    units = Column(Integer, default=1, nullable=False)
    # Relationships
    product = relationship('Product', back_populates='specifications')


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
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    lot_number = Column(String(255), nullable=False)
    expiration_date = Column(Date, nullable=True)
    amount = Column(Integer, default=0, nullable=False)
    # Relationships
    stock = relationship('Stock', back_populates='stock_products')
    product = relationship('Product',
                           backref=backref('stock_products',
                                           cascade='all, delete-orphan'))


class Order(Base):
    __tablename__ = 'orders'
    # Columns
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='SET NULL'), nullable=True)
    invoice = Column(String(255), nullable=True)
    invoice_type = Column(String(255), nullable=True)
    invoice_value = Column(Numeric(12, 2), nullable=True)
    financier = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Relationships
    user = relationship('User')


# Rename to Item
class OrderItem(Base):
    __tablename__ = 'order_items'
    __table_args__ = (UniqueConstraint(
        'item_id', 'order_id', 'lot_number', name='unique_order_item'), )
    # Columns
    # TODO: rename it to specification_id
    item_id = Column(Integer, ForeignKey(
        'specifications.id', ondelete='SET NULL'), nullable=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    amount = Column(Integer, default=1, nullable=False)
    lot_number = Column(String(255), nullable=False)
    expiration_date = Column(
        Date, default=datetime.utcnow().date, nullable=True)
    # TODO: delete it (unused)
    added_to_stock = Column(Boolean, default=False, nullable=True)
    # Relationships
    # TODO: rename to specification
    item = relationship('Specification')
    order = relationship('Order',
                         backref=backref('order_items',
                                         cascade='all, delete-orphan'))


# TODO: refactor Transaction
# TODO: Define cascade rules after refactoring
class Transaction(Base, TimeStampedModelMixin):
    __tablename__ = 'transactions'
    # Columns
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='SET NULL'), nullable=True)
    product_id = Column(Integer, ForeignKey(
        'products.id', ondelete='SET NULL'), nullable=True)
    stock_id = Column(Integer, ForeignKey(
        'stocks.id', ondelete='SET NULL'), nullable=True)
    lot_number = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False)
    category = db.Column(Integer, nullable=False)
    # Relationships
    user = relationship('User')
    product = relationship('Product')
    stock = relationship('Stock')
    # Constraints
    __table_args__ = (
        CheckConstraint(amount > 0, name='amount_is_positive'), {})
