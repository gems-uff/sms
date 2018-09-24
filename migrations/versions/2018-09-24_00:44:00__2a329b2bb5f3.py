"""empty message

Revision ID: 2a329b2bb5f3
Revises: 0e073e79f2d3
Create Date: 2018-09-24 00:44:00.188683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a329b2bb5f3'
down_revision = '0e073e79f2d3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('stock_minimum', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('specifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('manufacturer', sa.String(length=128), nullable=True),
        sa.Column('catalog_number', sa.String(length=128), nullable=True),
        sa.Column('units', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'manufacturer', 'catalog_number', name='unique_specification')
    )


def downgrade():
    op.drop_table('specifications')
    op.drop_table('products')
