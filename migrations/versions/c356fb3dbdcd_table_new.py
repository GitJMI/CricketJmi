"""migrate integer ids to uuid strings

Revision ID: c356fb3dbdcd
Revises: a647136c660a
Create Date: 2026-04-05 14:07:19.665474

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = 'c356fb3dbdcd'
down_revision = 'a647136c660a'
branch_labels = None
depends_on = None


def _legacy_uuid(old_user_id):
    if old_user_id is None:
        return None
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"legacy-user-{old_user_id}"))


def upgrade():
    connection = op.get_bind()

    op.add_column('users', sa.Column('id_uuid', sa.String(length=36), nullable=True))
    op.add_column('messages', sa.Column('id_uuid', sa.String(length=36), nullable=True))
    op.add_column('messages', sa.Column('user_id_uuid', sa.String(length=36), nullable=True))
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

    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('messages_pkey', 'messages', type_='primary')

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
    connection = op.get_bind()

    op.add_column('users', sa.Column('id_int', sa.Integer(), nullable=True))
    op.add_column('messages', sa.Column('id_int', sa.Integer(), nullable=True))
    op.add_column('messages', sa.Column('user_id_int', sa.Integer(), nullable=True))
    op.add_column('subscriptions', sa.Column('user_id_int', sa.Integer(), nullable=True))

    users = connection.execute(sa.text('SELECT id FROM users ORDER BY created_at NULLS FIRST, id')).fetchall()
    user_uuid_to_int = {}
    for idx, row in enumerate(users, start=1):
        user_uuid = row[0]
        user_uuid_to_int[user_uuid] = idx
        connection.execute(
            sa.text('UPDATE users SET id_int = :id_int WHERE id = :id_uuid'),
            {'id_int': idx, 'id_uuid': user_uuid},
        )

    messages = connection.execute(sa.text('SELECT id, user_id FROM messages ORDER BY created_at NULLS FIRST, id')).fetchall()
    for idx, row in enumerate(messages, start=1):
        message_uuid = row[0]
        user_uuid = row[1]
        connection.execute(
            sa.text('UPDATE messages SET id_int = :id_int, user_id_int = :user_id_int WHERE id = :id_uuid'),
            {
                'id_int': idx,
                'user_id_int': user_uuid_to_int.get(user_uuid),
                'id_uuid': message_uuid,
            },
        )

    subscriptions = connection.execute(sa.text('SELECT id, user_id FROM subscriptions ORDER BY id')).fetchall()
    for row in subscriptions:
        sub_id = row[0]
        user_uuid = row[1]
        connection.execute(
            sa.text('UPDATE subscriptions SET user_id_int = :user_id_int WHERE id = :sub_id'),
            {'user_id_int': user_uuid_to_int.get(user_uuid), 'sub_id': sub_id},
        )

    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('messages_pkey', 'messages', type_='primary')

    op.drop_column('users', 'id')
    op.alter_column('users', 'id_int', existing_type=sa.Integer(), nullable=False, new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])

    op.drop_column('messages', 'id')
    op.drop_column('messages', 'user_id')
    op.alter_column('messages', 'id_int', existing_type=sa.Integer(), nullable=False, new_column_name='id')
    op.alter_column('messages', 'user_id_int', existing_type=sa.Integer(), nullable=False, new_column_name='user_id')
    op.create_primary_key('messages_pkey', 'messages', ['id'])

    op.drop_column('subscriptions', 'user_id')
    op.alter_column('subscriptions', 'user_id_int', existing_type=sa.Integer(), nullable=False, new_column_name='user_id')
