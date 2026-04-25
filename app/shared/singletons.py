# shared/singletons.py
from app.modules.sessions.sessions_service import SessionsService
from app.modules.operations.operations_service import OperationsService

sessions_service = SessionsService()
audit_service = OperationsService()


# se usa asi:
# from app.shared.singletons import audit_service

"""
Login:
auth.router → llama service
service → sessions.service
repository → MongoDB

CRUD cliente:
clients.router
clients.service
audit.service → registra operación
"""