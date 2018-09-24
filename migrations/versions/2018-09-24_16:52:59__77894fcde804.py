"""empty message

Revision ID: 77894fcde804
Revises: 16b1a782cb5e
Create Date: 2018-09-24 16:52:59.924307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77894fcde804'
down_revision = '16b1a782cb5e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_on', sa.DateTime(), nullable=True),
        sa.Column('updated_on', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('stock_id', sa.Integer(), nullable=True),
        sa.Column('lot_number', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('category', sa.Integer(), nullable=False),
        sa.CheckConstraint('amount > 0', name='amount_is_positive'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('transactions')
