"""Initial migration - Create all CSB PostgreSQL tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-13

⚠️  This migration affects ONLY the CSB PostgreSQL database.
    HRM database is managed separately by Django.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Using String columns instead of PostgreSQL ENUM types (simpler migration)
    pass

    # Create csb_employee_refs table
    op.create_table(
        'csb_employee_refs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('hrm_employee_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('hrm_user_id', sa.Integer(), nullable=True),
        sa.Column('emp_code', sa.String(32), nullable=False, unique=True),
        sa.Column('username', sa.String(150), nullable=False, unique=True),
        sa.Column('full_name', sa.String(120), nullable=False),
        sa.Column('email', sa.String(254), nullable=True),
        sa.Column('department', sa.String(120), nullable=True),
        sa.Column('part', sa.String(120), nullable=True),
        sa.Column('role', sa.String(120), nullable=True),
        sa.Column('status', sa.String(32), server_default='Active'),
        sa.Column('join_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('photo', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Indexes for csb_employee_refs
    op.create_index('idx_hrm_employee_id', 'csb_employee_refs', ['hrm_employee_id'], unique=True)
    op.create_index('idx_emp_code', 'csb_employee_refs', ['emp_code'], unique=True)
    op.create_index('idx_username', 'csb_employee_refs', ['username'], unique=True)
    op.create_index('idx_status', 'csb_employee_refs', ['status'])
    op.create_index('idx_department', 'csb_employee_refs', ['department'])
    op.create_index('idx_is_active', 'csb_employee_refs', ['is_active'])
    op.create_index('idx_last_synced', 'csb_employee_refs', ['last_synced_at'])

    # Create crw_targets table
    op.create_table(
        'crw_targets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('target_type', sa.String(10), server_default='WEEK'),
        sa.Column('period_str', sa.String(7), nullable=True),
        sa.Column('operator_required', sa.Integer(), server_default='5'),
        sa.Column('leader_required', sa.Integer(), server_default='2'),
        sa.Column('pl_required', sa.Integer(), server_default='1'),
        sa.Column('tm_required', sa.Integer(), server_default='1'),
        sa.Column('gd_required', sa.Integer(), server_default='0'),
        sa.Column('reward_amount', sa.Float(), server_default='500000.0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_index('idx_target_type_period', 'crw_targets', ['target_type', 'period_str'], unique=True)
    op.create_index('idx_target_active', 'crw_targets', ['is_active'])
    
    # Add CHECK constraint for target_type
    op.execute("ALTER TABLE crw_targets ADD CONSTRAINT chk_target_type CHECK (target_type IN ('WEEK', 'MONTH', 'YEAR'))")

    # Create crw_connections table
    op.create_table(
        'crw_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('new_hire_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['connector_id'], ['csb_employee_refs.id'], ),
        sa.ForeignKeyConstraint(['new_hire_id'], ['csb_employee_refs.id'], ),
    )
    
    op.create_index('idx_connection_pair', 'crw_connections', ['new_hire_id', 'connector_id'], unique=True)
    op.create_index('idx_connection_status', 'crw_connections', ['status'])
    op.create_index('idx_connection_created', 'crw_connections', ['created_at'])
    
    op.execute("ALTER TABLE crw_connections ADD CONSTRAINT chk_connection_status CHECK (status IN ('PENDING', 'ACCEPTED', 'REJECTED'))")

    # Create crw_rewards table
    op.create_table(
        'crw_rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achieved_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(20), server_default='PENDING'),
        sa.Column('approved_by_ref_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['approved_by_ref_id'], ['csb_employee_refs.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['csb_employee_refs.id'], ),
        sa.ForeignKeyConstraint(['target_id'], ['crw_targets.id'], ),
    )
    
    op.create_index('idx_reward_employee_target', 'crw_rewards', ['employee_id', 'target_id'])
    op.create_index('idx_reward_status', 'crw_rewards', ['status'])
    op.create_index('idx_reward_achieved', 'crw_rewards', ['achieved_date'])
    
    op.execute("ALTER TABLE crw_rewards ADD CONSTRAINT chk_reward_status CHECK (status IN ('PENDING', 'APPROVED', 'FAILED'))")

    # Create crw_progress_snapshots table
    op.create_table(
        'crw_progress_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('snapshot_month', sa.String(7)),
        sa.Column('total_new_hires', sa.Integer(), server_default='0'),
        sa.Column('total_connections', sa.Integer(), server_default='0'),
        sa.Column('total_reward_amount', sa.Float(), server_default='0.0'),
        sa.Column('connections_by_dept', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_index('idx_snapshot_month', 'crw_progress_snapshots', ['snapshot_month'], unique=True)

    # Create csb_audit_logs table
    op.create_table(
        'csb_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('table_name', sa.String(50), nullable=False),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(10), nullable=False),
        sa.Column('changed_by_ref_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['changed_by_ref_id'], ['csb_employee_refs.id'], ),
    )
    
    op.create_index('idx_audit_table_record', 'csb_audit_logs', ['table_name', 'record_id'])
    op.create_index('idx_audit_action', 'csb_audit_logs', ['action'])
    op.create_index('idx_audit_changed_at', 'csb_audit_logs', ['changed_at'])
    
    op.execute("ALTER TABLE csb_audit_logs ADD CONSTRAINT chk_audit_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))")


def downgrade() -> None:
    # Drop tables in reverse order (dependencies first)
    op.drop_table('csb_audit_logs')
    op.drop_table('crw_progress_snapshots')
    op.drop_table('crw_rewards')
    op.drop_table('crw_connections')
    op.drop_table('crw_targets')
    op.drop_table('csb_employee_refs')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS auditaction')
    op.execute('DROP TYPE IF EXISTS rewardstatus')
    op.execute('DROP TYPE IF EXISTS connectionstatus')
    op.execute('DROP TYPE IF EXISTS targettype')
