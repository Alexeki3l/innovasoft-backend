from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.auth_router import router as auth_router
from app.modules.client.client_router import router as client_router
from app.modules.interest.interest_router import router as interest_router
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(
    title="Innovasoft API",
    description="API de gestión de clientes",
    version="1.0.0"
)

origins = [
    "https://warm-begonia-4bbab5.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(client_router, prefix="/api")
app.include_router(interest_router, prefix="/api")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
    
    
    
    
