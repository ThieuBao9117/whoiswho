"""Add entity, division, team, position fields to csb_employee_refs

Revision ID: 002_add_employee_org_fields
Revises: 001_initial
Create Date: 2026-04-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_employee_org_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('csb_employee_refs', sa.Column('entity', sa.String(120), nullable=True))
    op.add_column('csb_employee_refs', sa.Column('division', sa.String(120), nullable=True))
    op.add_column('csb_employee_refs', sa.Column('team', sa.String(120), nullable=True))
    op.add_column('csb_employee_refs', sa.Column('position', sa.String(120), nullable=True))
    op.create_index('idx_entity', 'csb_employee_refs', ['entity'])
    op.create_index('idx_division', 'csb_employee_refs', ['division'])
    op.create_index('idx_team', 'csb_employee_refs', ['team'])


def downgrade() -> None:
    op.drop_index('idx_team', 'csb_employee_refs')
    op.drop_index('idx_division', 'csb_employee_refs')
    op.drop_index('idx_entity', 'csb_employee_refs')
    op.drop_column('csb_employee_refs', 'position')
    op.drop_column('csb_employee_refs', 'team')
    op.drop_column('csb_employee_refs', 'division')
    op.drop_column('csb_employee_refs', 'entity')
