from datetime import datetime
from app.modules.operations.operations_repository import OperationsRepository

class OperationsService:
    def __init__(self):
        self.repo = OperationsRepository()

    async def log(self, accion, usuario, cliente_id, resultado):
        operation = {
            "accion": accion,
            "usuario": usuario,
            "cliente_id": cliente_id,
            "resultado": resultado,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.repo.insert(operation)