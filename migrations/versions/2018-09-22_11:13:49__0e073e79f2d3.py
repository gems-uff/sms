"""empty message

Revision ID: 0e073e79f2d3
Revises:
Create Date: 2018-09-22 11:13:49.052803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e073e79f2d3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pre_allowed_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=128), nullable=True),
        sa.Column('email', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('default', sa.Boolean(), nullable=True),
        sa.Column('permissions', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=64), nullable=True),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('confirmed', sa.Boolean(), nullable=True),
        sa.Column('stock_mail_alert', sa.Boolean(), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('pre_allowed_users')
