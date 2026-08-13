"""make appointments.scheduled_at timezone-aware

Revision ID: 8c9169acf192
Revises: ca896a0e610b
Create Date: 2026-08-13 14:28:16.455625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c9169acf192'
down_revision: Union[str, Sequence[str], None] = 'ca896a0e610b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'appointments', 'scheduled_at',
        type_=sa.DateTime(timezone=True),
        postgresql_using="scheduled_at AT TIME ZONE 'America/Chicago'",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'appointments', 'scheduled_at',
        type_=sa.DateTime(),
        postgresql_using="scheduled_at AT TIME ZONE 'America/Chicago'",
    )
