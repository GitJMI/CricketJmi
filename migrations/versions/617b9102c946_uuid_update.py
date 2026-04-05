"""uuid update

Revision ID: 617b9102c946
Revises: c356fb3dbdcd
Create Date: 2026-04-05 14:19:34.328254

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '617b9102c946'
down_revision = 'c356fb3dbdcd'
branch_labels = None
depends_on = None


def _has_column(inspector, table_name, column_name):
    return any(col['name'] == column_name for col in inspector.get_columns(table_name))


def _is_integer_column(inspector, table_name, column_name):
    for col in inspector.get_columns(table_name):
        if col['name'] == column_name:
            return isinstance(col['type'], sa.Integer)
    return False


def _legacy_uuid(old_user_id):
    if old_user_id is None:
        return None
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"legacy-user-{old_user_id}"))


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    required_tables = {'users', 'messages', 'subscriptions'}
    if not required_tables.issubset(set(inspector.get_table_names())):
        return

    # If this DB is already migrated to UUID IDs, this revision should be a no-op.
    if not _is_integer_column(inspector, 'users', 'id'):
        return

    if not _has_column(inspector, 'users', 'id_uuid'):
        op.add_column('users', sa.Column('id_uuid', sa.String(length=36), nullable=True))
    if not _has_column(inspector, 'messages', 'id_uuid'):
        op.add_column('messages', sa.Column('id_uuid', sa.String(length=36), nullable=True))
    if not _has_column(inspector, 'messages', 'user_id_uuid'):
        op.add_column('messages', sa.Column('user_id_uuid', sa.String(length=36), nullable=True))
    if not _has_column(inspector, 'subscriptions', 'user_id_uuid'):
        op.add_column('subscriptions', sa.Column('user_id_uuid', sa.String(length=36), nullable=True))

    users = connection.execute(sa.text('SELECT id FROM users')).fetchall()
    user_id_map = {}

    for row in users:
        old_user_id = row[0]
        new_user_id = str(uuid.uuid4())
        user_id_map[old_user_id] = new_user_id
        connection.execute(
            sa.text('UPDATE users SET id_uuid = :new_id WHERE id = :old_id'),
            {'new_id': new_user_id, 'old_id': old_user_id},
        )

    messages = connection.execute(sa.text('SELECT id, user_id FROM messages')).fetchall()
    for row in messages:
        old_message_id = row[0]
        old_user_id = row[1]
        new_message_id = str(uuid.uuid4())
        new_user_id = user_id_map.get(old_user_id) or _legacy_uuid(old_user_id)

        connection.execute(
            sa.text(
                'UPDATE messages SET id_uuid = :new_message_id, user_id_uuid = :new_user_id WHERE id = :old_message_id'
            ),
            {
                'new_message_id': new_message_id,
                'new_user_id': new_user_id,
                'old_message_id': old_message_id,
            },
        )

    subscriptions = connection.execute(sa.text('SELECT id, user_id FROM subscriptions')).fetchall()
    for row in subscriptions:
        sub_id = row[0]
        old_user_id = row[1]
        new_user_id = user_id_map.get(old_user_id) or _legacy_uuid(old_user_id)

        connection.execute(
            sa.text('UPDATE subscriptions SET user_id_uuid = :new_user_id WHERE id = :sub_id'),
            {'new_user_id': new_user_id, 'sub_id': sub_id},
        )

    op.execute(sa.text('ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey'))
    op.execute(sa.text('ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_pkey'))

    op.drop_column('users', 'id')
    op.alter_column('users', 'id_uuid', existing_type=sa.String(length=36), nullable=False, new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])

    op.drop_column('messages', 'id')
    op.drop_column('messages', 'user_id')
    op.alter_column('messages', 'id_uuid', existing_type=sa.String(length=36), nullable=False, new_column_name='id')
    op.alter_column('messages', 'user_id_uuid', existing_type=sa.String(length=36), nullable=False, new_column_name='user_id')
    op.create_primary_key('messages_pkey', 'messages', ['id'])

    op.drop_column('subscriptions', 'user_id')
    op.alter_column('subscriptions', 'user_id_uuid', existing_type=sa.String(length=36), nullable=False, new_column_name='user_id')


def downgrade():
    # Keeping downgrade a no-op to avoid destructive rollback of identifier migration.
    pass
