"""create locations and tags tables

Revision ID: a1b2c3d4e5f6
Revises: 6b8025cd418e
Create Date: 2026-03-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3d4e5f6'
down_revision = '6b8025cd418e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('label_ru', sa.String(200), nullable=False),
        sa.Column('group', sa.String(100), nullable=False),
        sa.Column('subgroup', sa.String(100), nullable=True),
    )

    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(150), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('lat', sa.Float, nullable=False),
        sa.Column('lng', sa.Float, nullable=False),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('region', sa.String(100), nullable=True, server_default='Краснодарский край'),
        sa.Column('photos', postgresql.ARRAY(sa.Text), nullable=False, server_default='{}'),
        sa.Column('price_from', sa.Integer, nullable=True),
        sa.Column('price_to', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='false'),
        sa.Column('is_featured', sa.Boolean, server_default='false'),
        sa.Column('seller_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('avg_temp_summer', sa.Float, nullable=True),
        sa.Column('avg_temp_winter', sa.Float, nullable=True),
        sa.Column('duration_hours_min', sa.Float, nullable=True),
        sa.Column('duration_hours_max', sa.Float, nullable=True),
        sa.Column('group_size_min', sa.Integer, nullable=True),
        sa.Column('group_size_max', sa.Integer, nullable=True),
    )

    op.create_table(
        'location_tags',
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('locations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('location_tags')
    op.drop_table('locations')
    op.drop_table('tags')
