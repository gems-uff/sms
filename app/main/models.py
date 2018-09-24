from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import Model

from app.extensions import db


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class TimeStampedModelMixin(db.Model):
    __abstract__ = True
    # Columns
    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Product(Base):
    __tablename__ = 'products'
    # Columns
    name = Column(String(128), nullable=False, unique=True)
    stock_minimum = Column(Integer, default=1, nullable=False)
    # Relationships
    specifications = relationship('Specification', back_populates='product')


class Specification(Base):
    __tablename__ = 'specifications'
    __table_args__ = (
        UniqueConstraint(
            'product_id', 'manufacturer', 'catalog_number',
            name='unique_specification'),
    )
    # Columns
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    manufacturer = Column(String(128), nullable=True)
    catalog_number = Column(String(128), nullable=True)
    units = Column(Integer, default=1, nullable=False)
    # Relationships
    product = relationship(
        'Product',
        back_populates='specifications',
        cascade='all, delete-orphan',
        single_parent=True)
