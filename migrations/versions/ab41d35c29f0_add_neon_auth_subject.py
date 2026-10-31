"""Add Neon Auth subject mapping to users.

Revision ID: ab41d35c29f0
Revises: e87c980e3db6
Create Date: 2026-10-30
"""
from alembic import op
import sqlalchemy as sa


revision = "ab41d35c29f0"
down_revision = "e87c980e3db6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("neon_auth_subject", sa.String(length=255)))
    op.create_index(
        "ix_user_neon_auth_subject",
        "user",
        ["neon_auth_subject"],
        unique=True,
    )


def downgrade():
    op.drop_index("ix_user_neon_auth_subject", table_name="user")
    op.drop_column("user", "neon_auth_subject")
