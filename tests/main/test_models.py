import pytest
import sqlalchemy.exc as sqlexc

from app.extensions import db
from app.main.models import Product, Specification


class TestProduct():
    def test_product_name_not_null(self, database):
        name = None
        p1 = Product(name=name)
        db.session.add(p1)
        with pytest.raises(sqlexc.IntegrityError):
            db.session.commit()

    def test_product_name_uniqueness(self, database):
        name = 'Produto'
        p1 = Product(name=name)
        p2 = Product(name=name)
        db.session.add(p1)
        db.session.add(p2)
        with pytest.raises(sqlexc.IntegrityError):
            db.session.commit()

    def test_product_stock_minimum_default_is_one(self, database):
        name = 'Produto'
        p1 = Product(name=name)
        db.session.add(p1)
        assert p1.stock_minimum is None
        db.session.commit()
        assert p1.stock_minimum is 1
