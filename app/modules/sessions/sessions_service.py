from datetime import datetime
from app.modules.sessions.sessions_repository import SessionsRepository

class SessionsService:
    def __init__(self):
        self.repo = SessionsRepository()

    async def create_session(self, session: dict):
        token = session.get("token") or session.get("accessToken") or session.get("access_token")
        userid = session.get("userid") or session.get("user_id") or session.get("id")
        username = session.get("username") or session.get("user") or session.get("name")

        if not all([token, userid, username]):
            raise ValueError(f"Faltan campos en session data: {list(session.keys())}")

        new_session = {
            "token": token,
            "userid": userid,
            "username": username,
            "login_timestamp": datetime.utcnow().isoformat()
        }

        await self.repo.create(new_session)
        return new_session

    async def logout(self, userid: str):
        await self.repo.delete(userid)