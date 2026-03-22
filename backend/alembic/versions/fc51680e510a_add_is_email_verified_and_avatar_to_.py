"""add is_email_verified and avatar to users

Revision ID: fc51680e510a
Revises: 39d632efabd7
Create Date: 2026-03-21 07:18:22.645017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fc51680e510a"
down_revision: Union[str, None] = "39d632efabd7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "users",
        sa.Column("avatar_object_name", sa.String(500), nullable=True),
    )
    # BUG FIX: keep server_default=func.now() so inserts without explicit
    # created_at don't fail. The original migration added the column then
    # immediately dropped the server_default, breaking all subsequent inserts.
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "created_at")
    op.drop_column("users", "avatar_object_name")
    op.drop_column("users", "is_email_verified")
