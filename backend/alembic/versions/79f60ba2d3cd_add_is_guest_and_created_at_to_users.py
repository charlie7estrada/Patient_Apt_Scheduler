"""add is_guest and created_at to users

Revision ID: 79f60ba2d3cd
Revises: 8c9169acf192
Create Date: 2026-09-14 20:18:23.625853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79f60ba2d3cd'
down_revision: Union[str, Sequence[str], None] = '8c9169acf192'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('is_guest', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        'users',
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_guest')
