"""ensure core tables exist

Revision ID: 9f4ab4d62fb1
Revises: 617b9102c946
Create Date: 2026-04-05 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '9f4ab4d62fb1'
down_revision = '617b9102c946'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    table_names = set(inspector.get_table_names())

    # Ensure enum exists before creating users table.
    role_enum = postgresql.ENUM('client', 'admin', name='user_roles')
    role_enum.create(connection, checkfirst=True)

    if 'users' not in table_names:
        op.create_table(
            'users',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('username', sa.String(length=100), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('password_hash', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column(
                'role',
                postgresql.ENUM('client', 'admin', name='user_roles', create_type=False),
                nullable=False,
                server_default='client',
            ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
            sa.UniqueConstraint('username'),
        )

    if 'messages' not in table_names:
        op.create_table(
            'messages',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('channel_id', sa.Integer(), nullable=True),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if 'subscriptions' not in table_names:
        op.create_table(
            'subscriptions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('plan', sa.String(length=50), nullable=True),
            sa.Column('start_date', sa.DateTime(), nullable=True),
            sa.Column('end_date', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    table_names = set(inspector.get_table_names())

    if 'subscriptions' in table_names:
        op.drop_table('subscriptions')
    if 'messages' in table_names:
        op.drop_table('messages')
    if 'users' in table_names:
        op.drop_table('users')
