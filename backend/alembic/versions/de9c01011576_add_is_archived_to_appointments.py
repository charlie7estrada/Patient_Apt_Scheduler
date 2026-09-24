"""add is_archived to appointments

Revision ID: de9c01011576
Revises: 79f60ba2d3cd
Create Date: 2026-09-23 19:57:31.277045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de9c01011576'
down_revision: Union[str, Sequence[str], None] = '79f60ba2d3cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'appointments',
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('appointments', 'is_archived')
