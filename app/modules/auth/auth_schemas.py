from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    expiration: str
    username: str
    userid: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    
class LogoutRequest(BaseModel):
    userid: str