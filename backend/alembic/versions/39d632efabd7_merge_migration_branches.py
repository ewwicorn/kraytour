"""merge migration branches

Revision ID: 39d632efabd7
Revises: a1b2c3d4e5f6, a39af2b753a0
Create Date: 2026-03-21 07:18:17.230731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39d632efabd7'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'a39af2b753a0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
