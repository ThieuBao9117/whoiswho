from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
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
    PENDING = "PENDING" # Pending HR approval
    APPROVED = "APPROVED" # HR approved
    FAILED = "FAILED"

class CRWTarget(Base):
    __tablename__ = "crw_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(Enum(TargetType), default=TargetType.WEEK)
    period_str = Column(String(7), nullable=True) # e.g. "2026-03"
    
    operator_required = Column(Integer, default=5)
    leader_required = Column(Integer, default=2)
    pl_required = Column(Integer, default=1)   # Part Leader
    tm_required = Column(Integer, default=1)   # Team Manager
    gd_required = Column(Integer, default=0)   # GD
    
    reward_amount = Column(Float, default=500000.0)
    is_active = Column(Boolean, default=True)

class CRWConnection(Base):
    __tablename__ = "crw_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    
    new_hire_id = Column(Integer, ForeignKey("hr_employee.id"), nullable=False)
    connector_id = Column(Integer, ForeignKey("hr_employee.id"), nullable=False)
    
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

    new_hire = relationship("Employee", foreign_keys=[new_hire_id])
    connector = relationship("Employee", foreign_keys=[connector_id])

class CRWReward(Base):
    __tablename__ = "crw_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("hr_employee.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("crw_targets.id"), nullable=False)
    
    achieved_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(RewardStatus), default=RewardStatus.PENDING)
    approved_by_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)
    notes = Column(String, nullable=True)
    
    employee = relationship("Employee", foreign_keys=[employee_id])
    target = relationship("CRWTarget")
    approved_by = relationship("AuthUser")

class CRWProgressSnapshot(Base):
    __tablename__ = "crw_progress_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_month = Column(String(7)) # e.g. "2026-03"
    
    total_new_hires = Column(Integer, default=0)
    total_connections = Column(Integer, default=0)
    total_reward_amount = Column(Float, default=0.0)
    
    connections_by_dept = Column(String, nullable=True) # JSON literal
    created_at = Column(DateTime, default=datetime.utcnow)
