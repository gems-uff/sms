import pytest
import sqlalchemy.exc as sqlexc

from app.extensions import db
from app.main.models import Product, Specification, Stock, StockProduct


class Test_Product():
    def test_product_name_not_null(self, database):
        name = None
        p1 = Product(name=name)
        db.session.add(p1)
        with pytest.raises(sqlexc.IntegrityError):
            db.session.commit()

    def test_product_name_uniqueness(self, database):
        name = 'Product'
        p1 = Product(name=name)
        p2 = Product(name=name)
        db.session.add(p1)
        db.session.add(p2)
        with pytest.raises(sqlexc.IntegrityError):
            db.session.commit()

    def test_product_stock_minimum_default_is_one(self, database):
        name = 'Product'
        p1 = Product(name=name)
        db.session.add(p1)
        assert p1.stock_minimum is None
        db.session.commit()
        assert p1.stock_minimum is 1


class Test_Specification():
    def test_units_default_is_one(self, database):
        p1 = Product(name='Product').create()
        spec1 = Specification(product_id=p1.id).create()
        assert spec1.units is 1


class Test_Product_Specification_Relationship():
    def test_specification_is_deleted_if_orphan(self, database):
        parent = Product(name='Product')
        child_1 = Specification(product=parent)
        parent.create()
        assert child_1.product_id == parent.id
        assert len(parent.specifications) is 1
        assert parent.specifications[0] == child_1
        parent.delete()
        assert not Specification.query.all()
        assert not Product.query.all()

    def test_constraint_unique_specification(self, database):
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
        with pytest.raises(sqlexc.IntegrityError):
            child_2.create()
        db.session.rollback()
        # Set another Product so it respects unique_specification
        child_2.product = Product(name='Another Product')
        child_2.create()
        assert child_2.product_id is not None


class Test_Stock():
    def test_stock_name_not_null(self, database):
        name = None
        stock = Stock(name=name)
        db.session.add(stock)
        with pytest.raises(sqlexc.IntegrityError):
            db.session.commit()

    def test_stock_name_unique(self, database):
        name = 'Stock Name'
        stock_1 = Stock(name=name)
        stock_2 = Stock(name=name)
        db.session.add(stock_1)
        db.session.add(stock_2)
        with pytest.raises(sqlexc.IntegrityError):
            db.session.commit()


class Test_StockProduct():
    pass


class Test_Stock_StockProduct_Relationship():
    pass
