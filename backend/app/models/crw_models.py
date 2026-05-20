"""
CRW Models - Connect Reward System
Independent database - No foreign keys to HRM tables

All employee references go through csb_employee_refs table.
Database: SQLite (development) / PostgreSQL (production)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Float, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from app.core.database import Base


class TargetType(str, enum.Enum):
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class ConnectionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class RewardStatus(str, enum.Enum):
    PENDING = "PENDING"      # Pending HR approval
    APPROVED = "APPROVED"    # HR approved
    FAILED = "FAILED"


class AuditAction(str, enum.Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class CRWTarget(Base):
    """Connection targets by period (week/month/year)"""
    __tablename__ = "crw_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_type = Column(Enum(TargetType), default=TargetType.MONTH)
    period_str = Column(String(7), nullable=True, index=True)  # e.g. "2026-03"

    operator_required = Column(Integer, default=5)
    leader_required = Column(Integer, default=2)
    pl_required = Column(Integer, default=1)   # Part Leader
    tm_required = Column(Integer, default=1)   # Team Manager
    gd_required = Column(Integer, default=0)   # GD

    reward_amount = Column(Float, default=500000.0)
    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rewards = relationship("CRWReward", back_populates="target")


class CRWConnection(Base):
    """Connection between new hire and connector"""
    __tablename__ = "crw_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References to csb_employee_refs (NOT HRM directly)
    new_hire_id = Column(Integer, ForeignKey("csb_employee_refs.id"), nullable=False, index=True)
    connector_id = Column(Integer, ForeignKey("csb_employee_refs.id"), nullable=False, index=True)

    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    new_hire = relationship("CSBEmployeeRef", foreign_keys=[new_hire_id])
    connector = relationship("CSBEmployeeRef", foreign_keys=[connector_id])


class CRWReward(Base):
    """Reward issued for achieving connection targets"""
    __tablename__ = "crw_rewards"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References to csb_employee_refs
    employee_id = Column(Integer, ForeignKey("csb_employee_refs.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("crw_targets.id"), nullable=False, index=True)

    achieved_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(RewardStatus), default=RewardStatus.PENDING, index=True)

    # Reference to auth user who approved (can be null if auto-approved)
    approved_by_ref_id = Column(Integer, ForeignKey("csb_employee_refs.id"), nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("CSBEmployeeRef", foreign_keys=[employee_id])
    target = relationship("CRWTarget", back_populates="rewards")
    approved_by = relationship("CSBEmployeeRef", foreign_keys=[approved_by_ref_id])


class CRWProgressSnapshot(Base):
    """Monthly statistics snapshots"""
    __tablename__ = "crw_progress_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_month = Column(String(7), unique=True, index=True)  # e.g. "2026-03"

    total_new_hires = Column(Integer, default=0)
    total_connections = Column(Integer, default=0)
    total_reward_amount = Column(Float, default=0.0)

    # JSON column for department breakdown (SQLite compatible)
    connections_by_dept = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class CSBAuditLog(Base):
    """Audit trail for all changes in CSB system"""
    __tablename__ = "csb_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)

    # Who made the change
    changed_by_ref_id = Column(Integer, ForeignKey("csb_employee_refs.id"), nullable=True)

    # Data before and after change (JSON as Text for SQLite)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)

    changed_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    changed_by = relationship("CSBEmployeeRef", foreign_keys=[changed_by_ref_id])
