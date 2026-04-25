from fastapi import APIRouter, HTTPException, Header
from app.shared.constants import LISTAR_INTERESES_URL
from app.shared.http_client import http_client

router = APIRouter(prefix="/interest", tags=["Interest"])


@router.get(
    "/listado",
    summary="Listar intereses",
    description="""
Retorna el catálogo completo de intereses disponibles en el sistema.

**Flujo:**
1. Valida que el header `Authorization` esté presente.
2. Extrae el Bearer token.
3. Realiza un GET al servicio externo (`LISTAR_INTERESES_URL`).
4. Retorna la respuesta directamente sin transformación.

**Uso:**
Este endpoint se usa típicamente para poblar el campo `interesFK` al momento de crear o actualizar un cliente.
El valor de `interesFK` debe ser uno de los IDs retornados por este listado.

**Notas:**
- No registra operación en MongoDB (solo lectura de catálogo).
- Solo captura `HTTPException`; errores inesperados del servicio externo se propagan sin envoltura.

**Header requerido:**
```
Authorization: Bearer <token>
```
    """,
    responses={
        200: {
            "description": "Catálogo de intereses retornado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": [
                            {"interesId": "1", "nombre": "Tecnología"},
                            {"interesId": "2", "nombre": "Deportes"},
                            {"interesId": "3", "nombre": "Arte"}
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Token ausente en el header Authorization.",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing token"}
                }
            }
        },
    }
)
async def list_interests(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing token")

        token = authorization.replace("Bearer ", "")

        response = await http_client.get(
            LISTAR_INTERESES_URL,
            token=token
        )

        return response

    except HTTPException as e:
        raise e
