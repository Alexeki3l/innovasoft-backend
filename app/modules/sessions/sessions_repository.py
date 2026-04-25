from app.db.mongo import db

class SessionsRepository:
    def __init__(self):
        self.collection = db.sesiones

    async def create(self, session: dict):
        result = await self.collection.insert_one(session)

        return result

    async def delete(self, userid: str):
        await self.collection.delete_one({"userid": str(userid)})