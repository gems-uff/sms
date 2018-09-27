from datetime import datetime

import pytest
import sqlalchemy.exc as sqlexc

from app.extensions import db

from app.auth.models import User
from app.main.models import (
    Base, Product, Specification, Stock, StockProduct, Order, OrderItem)


class TestBase():
    def test_repr(self, database):
        class ReprModel(Base):
            pass
        x = ReprModel(id=1)
        assert repr(x) == '<ReprModel (1)>'

    def test_str(self, database):
        class StrModel(Base):
            pass
        x = StrModel(id=1)
        assert str(x) == '<StrModel (1)>'


class Test_Product():
    def test_name_not_null(self, database):
        name = None
        p1 = Product(name=name)
        db.session.add(p1)
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*not-null.*'):
            db.session.commit()

    def test_name_unique(self, database):
        name = 'Product'
        p1 = Product(name=name)
        p2 = Product(name=name)
        db.session.add(p1)
        db.session.add(p2)
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*products_name_key.*'):
            db.session.commit()

    def test_stock_minimum_defaults_to_one(self, database):
        name = 'Product'
        p1 = Product(name=name)
        db.session.add(p1)
        assert p1.stock_minimum is None
        db.session.commit()
        assert p1.stock_minimum is 1


class Test_Specification():
    def test_units_defaults_to_one(self, database):
        p1 = Product(name='Product').create()
        spec1 = Specification(product_id=p1.id).create()
        assert spec1.units is 1

    def test_unique_specification_constraint(self, database):
        parent = Product(name='Product')
        child_1 = Specification(product=parent,
                                manufacturer='Manufacturer',
                                catalog_number='Catalog')
        db.session.add(parent)
        db.session.commit()
        # Create spec with invalid attributes (violates unique_specification)
        child_2 = Specification(product=parent,
                                manufacturer='Manufacturer',
                                catalog_number='Catalog')
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*unique_specification.*'):
            child_2.create()
        db.session.rollback()
        # Set another Product so it respects unique_specification
        child_2.product = Product(name='Another Product')
        child_2.create()
        assert child_2.product_id is not None


class Test_Product_Specification_Relationship():
    def test_product_delete_cascades_to_specifications(self, database):
        product = Product(name='Product')
        child_1 = Specification(product=product)
        child_2 = Specification(product=product)
        product.create()
        assert len(product.specifications) is 2
        assert child_1.product_id is product.id
        assert child_2.product_id is product.id
        product.delete()
        assert not Specification.query.all()
        assert not Product.query.all()


class Test_Stock():
    def test_name_not_null(self, database):
        name = None
        stock = Stock(name=name)
        db.session.add(stock)
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*not-null.*'):
            db.session.commit()

    def test_name_unique(self, database):
        name = 'Stock Name'
        stock_1 = Stock(name=name)
        stock_2 = Stock(name=name)
        db.session.add(stock_1)
        db.session.add(stock_2)
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*stocks_name_key.*'):
            db.session.commit()

    def test_insert_main_stock(self, database):
        Stock.insert_main_stock()
        assert len(Stock.query.all()) is 1
        Stock.insert_main_stock()
        assert len(Stock.query.all()) is 1


class Test_StockProduct():
    def test_lot_number_not_null(self, database):
        stock = Stock(name='Stock').create()
        product = Product(name='Product').create()
        lot_number = None
        stock_product = StockProduct(stock_id=stock.id,
                                     product_id=product.id,
                                     lot_number=lot_number)
        db.session.add(stock_product)
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*not-null.*'):
            db.session.commit()

    def test_amount_default_to_zero(self, database):
        stock = Stock(name='Stock').create()
        product = Product(name='Product').create()
        lot_number = 'Lot'
        stock_product = StockProduct(stock_id=stock.id,
                                     product_id=product.id,
                                     lot_number=lot_number)
        db.session.add(stock_product)
        db.session.commit()
        assert stock_product.amount is 0

    def test_unique_stock_product_constraint(self, database):
        stock = Stock(name='Stock').create()
        product = Product(name='Product').create()
        lot_number = 'Lot'
        stock_product_1 = StockProduct(stock_id=stock.id,
                                       product_id=product.id,
                                       lot_number=lot_number)
        stock_product_2 = StockProduct(stock_id=stock.id,
                                       product_id=product.id,
                                       lot_number=lot_number)
        db.session.add(stock_product_1)
        db.session.add(stock_product_2)
        with pytest.raises(sqlexc.IntegrityError,
                           match=r'.*unique_stock_product.*'):
            db.session.commit()
        db.session.rollback()
        db.session.add(stock_product_1)
        stock_product_2.lot_number = 'Lot_2'
        db.session.add(stock_product_2)
        db.session.commit()


class Test_Stock_StockProduct_Relationship():
    def test_stock_delete_cascades_to_stock_products(self, database):
        stock = Stock(name='Stock')
        product = Product(name='Product')
        stock_product_1 = StockProduct(stock=stock,
                                       product=product,
                                       lot_number='Lot 1')
        stock_product_2 = StockProduct(stock=stock,
                                       product=product,
                                       lot_number='Lot 2')
        stock.create()
        assert len(stock.stock_products) is 2
        assert stock_product_1.stock_id is stock.id
        assert stock_product_2.stock_id is stock.id
        stock.delete()
        assert not StockProduct.query.all()
        assert not Stock.query.all()


class Test_StockProduct_Product_Relationship():
    def test_product_delete_cascades_to_stock_products(self, database):
        stock = Stock(name='Stock')
        product = Product(name='Product')
        stock_product_1 = StockProduct(stock=stock,
                                       product=product,
                                       lot_number='Lot 1')
        stock_product_2 = StockProduct(stock=stock,
                                       product=product,
                                       lot_number='Lot 2')
        product.create()
        assert len(StockProduct.query.all()) is 2
        assert stock_product_1.product_id is product.id
        assert stock_product_2.product_id is product.id
        product.delete()
        assert not StockProduct.query.all()
        assert not Product.query.all()


class Test_Order():
    def test_save_order_to_database(self, database):
        order = Order()
        db.session.add(order)
        db.session.commit()
        order.order_date <= datetime.utcnow()


class Test_Order_OrderItem_Relationship():
    def test_delete_order_cascades_to_order_items(self, database):
        order = Order()
        product = Product(name='Product')
        specification = Specification(product=product)
        order_item_1 = OrderItem(item=specification,
                                 order=order,
                                 lot_number='lot_1')
        order_item_2 = OrderItem(item=specification,
                                 order=order,
                                 lot_number='lot_2')
        order.create()
        assert len(order.order_items) is 2
        assert order_item_1.order_id is order.id
        assert order_item_2.order_id is order.id
        order.delete()
        assert not OrderItem.query.all()


class Test_Order_User_Relationship():
    def test_delete_user_cascades_setnull(self, database):
        order = Order()
        user = User(email='user@user.com')
        order.user = user
        db.session.add(order)
        db.session.commit()
        assert order.user_id is user.id
        assert order.user is user
        db.session.delete(user)
        db.session.commit()
        assert order.user is None
        assert order.user_id is None


class Test_OrderItem():
    def test_non_unique_order_item_constraint(self, database):
        order = Order()
        product = Product(name='Product')
        specification = Specification(product=product)
        order_item_1 = OrderItem(
            item=specification, order=order, lot_number='lot_1')
        order_item_2 = OrderItem(
            item=specification, order=order, lot_number='lot_1')
        db.session.add(order_item_1)
        db.session.add(order_item_2)
        db.session.commit()
        assert order_item_1.lot_number == 'lot_1'
        assert order_item_2.lot_number == 'lot_1'


class Test_OrderItem_Specification_Relationship():
    def test_delete_specification_cascades_setnull(self, database):
        order = Order()
        product = Product(name='Product')
        specification = Specification(product=product)
        order_item = OrderItem(
            item=specification, order=order, lot_number='lot')
        db.session.add(order)
        db.session.commit()
        assert order_item.item_id is specification.id
        specification.delete()
        assert order_item.item_id is None
        assert order_item.item is None


@pytest.mark.skip
class Test_Transaction_Relationships():
    # TODO: tests for transaction after refactoring it
    def test_user(self, database):
        pass

    def test_product(self, database):
        pass

    def test_stock(self, database):
        pass
