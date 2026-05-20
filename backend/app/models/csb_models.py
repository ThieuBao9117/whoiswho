"""
CSB Database Models - All models for the independent CSB database

Import tất cả models từ đây để SQLAlchemy Alembic nhận diện đúng.
"""
from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import (
    CRWTarget,
    CRWConnection,
    CRWReward,
    CRWProgressSnapshot,
    CSBAuditLog,
)

__all__ = [
    "CSBEmployeeRef",
    "CRWTarget",
    "CRWConnection",
    "CRWReward",
    "CRWProgressSnapshot",
    "CSBAuditLog",
]
