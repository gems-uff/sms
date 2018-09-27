import jsonpickle
from flask import session

from app.extensions import db
from app.main.models import (Stock, StockProduct, Product,
                             Order, OrderItem, Specification, Transaction)
from app.auth.models import User


def get_stock(stock_id=None):
    if stock_id:
        return Stock.query.get(stock_id)
    else:
        return Stock.query.first()


def get_products_in_stock(stock):
    products = db.session.query(Product).join(StockProduct).filter_by(
        stock_id=stock.id).order_by(Product.name).all()
    for p in products:
        p.total = stock.total(p)
    return products


def get_specifications():
    return db.session.query(Specification).join(Product).order_by(
        Product.name).all()

def create_add_transactions_from_order(order, stock):
    user = order.user
    for order_item in order.order_items:
        product = order_item.item.product
        lot_number = order_item.lot_number
        total_units = order_item.amount * order_item.item.units
        transaction = Transaction()
        transaction.user = user
        transaction.product = product
        transaction.lot_number = lot_number
        transaction.amount = total_units
        transaction.stock = stock
        transaction.category = Transaction.ADD
        db.session.add(transaction)
    db.session.commit()


def create_sub_transaction(user, product, lot_number, amount, stock):
    transaction = Transaction()
    transaction.user = user
    transaction.product = product
    transaction.lot_number = lot_number
    transaction.amount = amount
    transaction.stock = stock
    transaction.category = Transaction.SUB

    db.session.add(transaction)
    db.session.commit()


def get_product_by_name(name):
    return Product.query.filter_by(name=name).first()


def create_product(name):
    product = Product(name=name)
    db.session.add(product)
    db.session.commit()
    return product


def get_order_items_from_session():
    if not session.get('order_items'):
        session['order_items'] = []
        return []
    else:
        return [jsonpickle.decode(item) for item in session.get('order_items')]


def add_order_item_to_session(order_item):
    # See http://flask.pocoo.org/docs/0.12/api/#sessions
    # Must be manually set
    if not session.get('order_items'):
        session['order_items'] = []
    session['order_items'] += [order_item.toJSON()]
    session.modified = True


def clear_order_items_session():
    if not session.get('order_items'):
        session['order_items'] = []
    session['order_items'] = []
