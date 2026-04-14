import uuid
import json
from typing import Optional, Any
from db import SessionLocal
from models import AuditLog

def log_audit_event(
    action: str,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[Any] = None
):
    """
    Persists an enterprise audit event for governance and compliance.
    """
    db = SessionLocal()
    try:
        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_id=resource_id,
            metadata_json=metadata if isinstance(metadata, dict) else {"data": str(metadata)} if metadata else None
        )
        db.add(log)
        db.commit()
    except Exception as e:
        # We don't want audit logging failures to crash the primary request
        print(f"FAILED TO STORE AUDIT LOG: {e}")
    finally:
        db.close()
