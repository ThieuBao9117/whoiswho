"""Expand photo column to VARCHAR(500) to support long HRM photo URLs

Revision ID: 003_expand_photo_column
Revises: 002_add_employee_org_fields
Create Date: 2026-05-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_expand_photo_column'
down_revision: Union[str, None] = '002_add_employee_org_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Increase photo column from VARCHAR(100) to VARCHAR(500)
    op.alter_column(
        'csb_employee_refs',
        'photo',
        existing_type=sa.String(100),
        type_=sa.String(500),
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        'csb_employee_refs',
        'photo',
        existing_type=sa.String(500),
        type_=sa.String(100),
        existing_nullable=True
    )
