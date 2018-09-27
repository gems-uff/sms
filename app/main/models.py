import jsonpickle
from datetime import datetime

from sqlalchemy import (Column, Integer, String, DateTime, UniqueConstraint,
                        ForeignKey, Date, Numeric, Boolean, CheckConstraint)
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import Model

from app.extensions import db
from app.logger import logger


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

    def toJSON(self):
        return jsonpickle.encode(self)

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
        stock = Stock.query.first()
        if not stock:
            stock = Stock(name='main').create()

    def total(self, product):
        total = 0
        for sp in self.stock_products:
            if sp.product_id == product.id:
                total += sp.amount
        return total

    def get_in_stock(self, product, lot_number):
        for stock_product in self.stock_products:
            if stock_product.product == product \
                    and stock_product.lot_number == lot_number:
                return stock_product
        return None

    def has_enough(self, product, lot_number, amount):
        if amount < 1:
            raise ValueError('Amount must be greater than 0')
        in_stock = self.get_in_stock(product, lot_number)
        if in_stock is None or in_stock.amount < amount:
            return False
        return True

    def add(self, product, lot_number, expiration_date, amount):
        if amount < 1 or isinstance(amount, int) is False:
            raise ValueError('Amount must be a positive integer')
        stock_product = self.get_in_stock(product, lot_number)
        if stock_product is None:
            stock_product = StockProduct(
                stock=self,
                product=product,
                lot_number=lot_number,
                expiration_date=expiration_date,
                amount=0    )
        else:
            if expiration_date != stock_product.expiration_date:
                logger.warning('Different expiration date, updating...')
        stock_product.expiration_date = expiration_date
        stock_product.amount += amount
        db.session.add(stock_product)

    def subtract(self, product, lot_number, amount):
        """
        amount: total units to be subtracted
        """
        if amount < 1 or isinstance(amount, int) is False:
            raise ValueError('Amount must be a positive integer')
        in_stock = self.get_in_stock(product, lot_number)
        if in_stock is None:
            raise ValueError('There is no {} in stock'.format(product.name))
        if self.has_enough(product, lot_number, amount):
            in_stock.amount -= amount
            return True
        raise ValueError('Not enough in stock')


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
class OrderItem(Base, TimeStampedModelMixin):
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
# - Add OrderItem dependency (1 to 1, uselist=False)
# - Add StockProduct dependency (many to one)
# - Split in two different Transactions?
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
    category = Column(Integer, nullable=False)
    # Relationships
    user = relationship('User')
    product = relationship('Product')
    stock = relationship('Stock')
    # Constraints
    __table_args__ = (
        CheckConstraint(amount > 0, name='amount_is_positive'), {})
    # Attributes
    ADD = 1
    SUB = 2
