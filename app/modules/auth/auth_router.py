from fastapi import APIRouter, HTTPException
from app.modules.auth.auth_schemas import LoginRequest, RegisterRequest, LogoutRequest
from app.modules.sessions.sessions_service import SessionsService
from app.shared.http_client import http_client
from app.shared.constants import *

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    summary="Registrar nuevo usuario",
    description="""
Crea una cuenta nueva en el sistema.

**Flujo:**
1. Recibe `username`, `password` y `email`.

    """,
    status_code=200,
    responses={
        200: {
            "description": "Usuario registrado exitosamente.",
            "content": {
                "application/json": {
                    "example": {"message": "User registered successfully"}
                }
            }
        },
        400: {
            "description": "El servicio externo rechazó el registro (usuario/email ya existe, datos inválidos, etc.).",
            "content": {
                "application/json": {
                    "example": {"detail": "Ya existe un usuario con esos datos."}
                }
            }
        },
    }
)
async def register(body: RegisterRequest):
    try:
        payload = body.model_dump()
        response = await http_client.post(REGISTER_URL, json=payload)

        if response.get("status") == "Error":
            raise HTTPException(
                status_code=400,
                detail=response.get("message")
            )

        return {"message": "User registered successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con esos datos."
        )


@router.post(
    "/login",
    summary="Iniciar sesión",
    description="""
Autentica al usuario y persiste su sesión en MongoDB.

**Flujo:**
1. Recibe `username` y `password`.
2. Llama al servicio externo (`LOGIN_URL`).
3. Si las credenciales son inválidas, el servicio externo responde `status == "Error"` → HTTP 400.
4. Si el login es exitoso, guarda la sesión en MongoDB (colección `sesiones`) con `token`, `userid`, `username` y `login_timestamp`.
5. Retorna la respuesta completa del servicio externo (incluye token y datos de sesión).

**Notas:**
- El token retornado debe usarse en el header `Authorization: Bearer <token>` para los endpoints protegidos.
- En caso de error inesperado (ej. MongoDB caído), retorna HTTP 400.
    """,
    responses={
        200: {
            "description": "Login exitoso. Retorna token y datos de sesión.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "token": "eyJhbGciOi...",
                            "expiration": "2024-12-31T23:59:59",
                            "username": "johndoe",
                            "userid": "abc123"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Credenciales inválidas o error al persistir la sesión.",
            "content": {
                "application/json": {
                    "example": {"detail": "Credenciales inválidas"}
                }
            }
        },
    }
)
async def login(body: LoginRequest):
    try:
        payload = body.model_dump()

        response = await http_client.post(LOGIN_URL, json=payload)

        print("LOGIN RESPONSE:", response, flush=True)

        status = response.get("status")
        data = response.get("data")
        error = response.get("error") or response.get("text")

        # 🔥 validar error del backend externo
        if status and status >= 400:
            raise HTTPException(
                status_code=status,
                detail=error or "Error en login"
            )

        if not data:
            raise HTTPException(
                status_code=400,
                detail="Respuesta inválida del servidor"
            )

        sessionService = SessionsService()
        await sessionService.create_session(data)

        return {
            "message": "Login exitoso",
            "data": data
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("LOGIN ERROR:", str(e), flush=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="""
Cierra la sesión activa de un usuario eliminando su registro de MongoDB.

**Flujo:**
1. Recibe el `userid` del usuario.
2. Elimina el documento de sesión correspondiente en MongoDB (colección `sesiones`) filtrando por `userid`.
3. Retorna confirmación del cierre de sesión.

**Notas:**
- No invalida el token JWT en el servicio externo; solo limpia la sesión local en MongoDB.
- Si el `userid` no existe en MongoDB, la operación igualmente retorna éxito (delete_one no lanza error si no encuentra).
    """,
    responses={
        200: {
            "description": "Sesión cerrada exitosamente.",
            "content": {
                "application/json": {
                    "example": {"details": "User logged out successfully"}
                }
            }
        },
        400: {
            "description": "Error inesperado al cerrar sesión.",
            "content": {
                "application/json": {
                    "example": {"detail": "Error al cerrar sesión."}
                }
            }
        },
    }
)
async def logout(body: LogoutRequest):
    try:
        sessionService = SessionsService()
        await sessionService.logout(body.userid)

        return {"details": "User logged out successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
