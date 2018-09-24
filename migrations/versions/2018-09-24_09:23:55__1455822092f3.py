"""empty message

Revision ID: 1455822092f3
Revises: 2a329b2bb5f3
Create Date: 2018-09-24 09:23:55.971297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1455822092f3'
down_revision = '2a329b2bb5f3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('stock_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('lot_number', sa.String(length=255), nullable=False),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stock_id', 'product_id', 'lot_number',
                            name='unique_stock_product')
    )
    op.alter_column('products', 'name',
                    existing_type=sa.VARCHAR(length=128),
                    type_=sa.String(length=255),
                    existing_nullable=False)
    op.alter_column('specifications', 'catalog_number',
                    existing_type=sa.VARCHAR(length=128),
                    type_=sa.String(length=255),
                    existing_nullable=True)
    op.alter_column('specifications', 'manufacturer',
                    existing_type=sa.VARCHAR(length=128),
                    type_=sa.String(length=255),
                    existing_nullable=True)


def downgrade():
    op.alter_column('specifications', 'manufacturer',
                    existing_type=sa.String(length=255),
                    type_=sa.VARCHAR(length=128),
                    existing_nullable=True)
    op.alter_column('specifications', 'catalog_number',
                    existing_type=sa.String(length=255),
                    type_=sa.VARCHAR(length=128),
                    existing_nullable=True)
    op.alter_column('products', 'name',
                    existing_type=sa.String(length=255),
                    type_=sa.VARCHAR(length=128),
                    existing_nullable=False)
    op.drop_table('stock_products')
    op.drop_table('stocks')
