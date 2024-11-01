from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.auth.auth_cookie import auth_backend, fastapi_users
from src.auth.models import User
from src.auth.refs_routers import refs_router
from src.auth.schemas import UserRead, UserCreate

app = FastAPI(title="Refs_app")
current_user = fastapi_users.current_user()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

@app.get("/api/auth/check")
async def check_authentication(user: User = Depends(current_user)):
    return {"email": user.email}

@app.get("/", response_class=HTMLResponse)
async def serve_react_app():
    index_path = Path("static/index.html")
    return index_path.read_text()

# Маршрут для статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(refs_router, tags=["Refs"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT","*"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization","*"],
)

