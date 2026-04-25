from datetime import datetime
from app.modules.sessions.sessions_repository import SessionsRepository

class SessionsService:
    def __init__(self):
        self.repo = SessionsRepository()

    async def create_session(self, session: dict):
        session = {
            "token": session["token"],
            "userid": session["userid"],
            "username": session["username"],
            "login_timestamp": datetime.utcnow().isoformat()
        }
        await self.repo.create(session)
        return session

    async def logout(self, userid: str):
        await self.repo.delete(userid)