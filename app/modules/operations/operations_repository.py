from app.db.mongo import db

class OperationsRepository:
    def __init__(self):
        self.collection = db.operaciones

    async def insert(self, operation: dict):
        await self.collection.insert_one(operation)