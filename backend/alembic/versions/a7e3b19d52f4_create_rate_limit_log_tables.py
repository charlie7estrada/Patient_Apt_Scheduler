"""create rate limit log tables

Revision ID: a7e3b19d52f4
Revises: c4d0f9e8c53e
Create Date: 2026-10-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7e3b19d52f4'
down_revision: Union[str, Sequence[str], None] = 'c4d0f9e8c53e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'chat_message_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chat_message_log_id'), 'chat_message_log', ['id'], unique=False)
    op.create_index('ix_chat_message_log_user_id_created_at', 'chat_message_log', ['user_id', 'created_at'], unique=False)

    op.create_table(
        'guest_creation_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ip', sa.String(length=45), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_guest_creation_log_id'), 'guest_creation_log', ['id'], unique=False)
    op.create_index('ix_guest_creation_log_ip_created_at', 'guest_creation_log', ['ip', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_guest_creation_log_ip_created_at', table_name='guest_creation_log')
    op.drop_index(op.f('ix_guest_creation_log_id'), table_name='guest_creation_log')
    op.drop_table('guest_creation_log')

    op.drop_index('ix_chat_message_log_user_id_created_at', table_name='chat_message_log')
    op.drop_index(op.f('ix_chat_message_log_id'), table_name='chat_message_log')
    op.drop_table('chat_message_log')
