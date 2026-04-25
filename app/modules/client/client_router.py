from fastapi import APIRouter, Header, HTTPException
from app.shared.http_client import http_client
from app.modules.client.client_schemas import ListRequest, CreateRequest
from app.modules.operations.operations_service import OperationsService
from app.shared.constants import *

router = APIRouter(prefix="/client", tags=["Clients"])


@router.post(
    "/listado",
    summary="Listar clientes",
    description="""
Retorna el listado de clientes registrados en el sistema.

**Flujo:**
1. Valida que el header `Authorization` esté presente.
2. Extrae el Bearer token y lo reenvía al servicio externo (`LISTAR_CLIENTES_URL`).
3. Si el servicio externo responde con `status == "Error"`, retorna HTTP 400.
4. Registra la operación en MongoDB (colección `operaciones`) con acción `LISTAR_CLIENTES`.
5. Retorna la respuesta del servicio externo.

**Filtros opcionales (body):**
- `identificacion`: filtra por número de identificación exacto.
- `nombre`: filtra por nombre del cliente.
- `usuarioId` *(requerido)*: identificador del usuario que realiza la consulta (se usa para auditoría).

**Header requerido:**
```
Authorization: Bearer <token>
```
    """,
    responses={
        200: {
            "description": "Listado de clientes retornado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": [
                            {"clienteId": "1", "nombre": "Juan", "identificacion": "12345678"}
                        ]
                    }
                }
            }
        },
        400: {"description": "Error retornado por el servicio externo."},
        401: {
            "description": "Token ausente.",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing token"}
                }
            }
        },
    }
)
async def list_client(
    body: ListRequest,
    authorization: str = Header(None)
):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing token")

        token = authorization.replace("Bearer ", "")

        response = await http_client.post(
            LISTAR_CLIENTES_URL,
            json=body.model_dump(),
            token=token
        )

        if response.get("status") == "Error":
            raise HTTPException(
                status_code=400,
                detail=response.get("message")
            )

        operationService = OperationsService()
        await operationService.log(
            accion="LISTAR_CLIENTES",
            usuario=body.usuarioId,
            cliente_id=None,
            resultado=response.get("status")
        )

        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/crear",
    summary="Crear cliente",
    description="""
Crea un nuevo cliente en el sistema con todos sus datos personales.

**Flujo:**
1. Valida que el header `Authorization` esté presente.
2. Extrae el Bearer token.
3. Envía todos los campos del body al servicio externo (`CREAR_CLIENTE_URL`).
4. Si el servicio externo retorna un status >= 400, lanza la excepción con ese mismo status code.
5. Registra la operación en MongoDB (colección `operaciones`) con acción `CREAR`, siempre en el bloque `finally` (incluso si hubo error).
6. Retorna mensaje de éxito y la respuesta del servicio externo.

**Campos del body:**

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | string | Nombre del cliente |
| `apellidos` | string | Apellidos del cliente |
| `identificacion` | string | Número de identificación |
| `celular` | string | Número de celular principal |
| `otroTelefono` | string | Teléfono alternativo |
| `direccion` | string | Dirección de residencia |
| `fNacimiento` | datetime | Fecha de nacimiento (ISO 8601) |
| `fAfiliacion` | datetime | Fecha de afiliación (ISO 8601) |
| `sexo` | string | Sexo del cliente (`M` o `F`) |
| `resennaPersonal` | string | Descripción o reseña personal |
| `imagen` | string | URL o base64 de la imagen de perfil |
| `interesFK` | string | ID del interés asociado |
| `usuarioId` | string | ID del usuario que registra el cliente |

**Header requerido:**
```
Authorization: Bearer <token>
```
    """,
    status_code=201,
    responses={
        201: {
            "description": "Cliente creado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Cliente creado exitosamente",
                        "data": {"status": 201, "data": {"clienteId": "abc123"}}
                    }
                }
            }
        },
        400: {"description": "Error retornado por el servicio externo."},
        401: {
            "description": "Token ausente.",
            "content": {"application/json": {"example": {"detail": "Token requerido"}}}
        },
        500: {"description": "Error interno inesperado."},
    }
)
async def create_client(
    body: CreateRequest,
    authorization: str = Header(None)
):
    operations_service = OperationsService()
    status_result = None
    response = None

    try:
        if not authorization or not authorization.strip():
            status_result = 401
            raise HTTPException(status_code=401, detail="Token requerido")

        token = authorization.replace("Bearer ", "").strip()

        response = await http_client.post(
            CREAR_CLIENTE_URL,
            json=body.model_dump(mode="json"),
            token=token
        )

        status_result = response.get("status")

        if status_result >= 400:
            raise HTTPException(
                status_code=status_result,
                detail=response.get("data") or "Error al crear cliente"
            )

        return {
            "message": "Cliente creado exitosamente",
            "data": response
        }

    except HTTPException as e:
        status_result = e.status_code
        raise e

    except Exception as e:
        status_result = 500
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        await operations_service.log(
            accion="CREAR",
            usuario=body.usuarioId,
            cliente_id=body.usuarioId,
            resultado=str(status_result)
        )


@router.patch(
    "/update",
    summary="Actualizar cliente",
    description="""
Actualiza los datos de un cliente existente en el sistema.

**Flujo:**
1. Valida que el header `Authorization` esté presente.
2. Extrae el Bearer token.
3. Envía el body completo al servicio externo (`EDITAR_CLIENTE_URL`).
4. Si el servicio externo retorna un status >= 400, lanza la excepción con ese mismo status code.
5. Registra la operación en MongoDB (colección `operaciones`) con acción `ACTUALIZAR`, siempre en el bloque `finally`.

**Notas:**
- Usa el mismo schema `CreateRequest` que `/crear`. Se deben enviar todos los campos.
- `usuarioId` es el ID del usuario que realiza la actualización (se registra en auditoría como `cliente_id`).

**Header requerido:**
```
Authorization: Bearer <token>
```
    """,
    responses={
        200: {
            "description": "Cliente actualizado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Cliente creado exitosamente",
                        "data": {"status": 200, "data": {"clienteId": "abc123"}}
                    }
                }
            }
        },
        400: {"description": "Error retornado por el servicio externo."},
        401: {
            "description": "Token ausente.",
            "content": {"application/json": {"example": {"detail": "Token requerido"}}}
        },
        500: {"description": "Error interno inesperado."},
    }
)
async def update_client(
    body: CreateRequest,
    authorization: str = Header(None)
):
    operations_service = OperationsService()
    status_result = None

    try:
        if not authorization or not authorization.strip():
            status_result = 401
            raise HTTPException(status_code=401, detail="Token requerido")

        token = authorization.replace("Bearer ", "").strip()

        response = await http_client.post(
            EDITAR_CLIENTE_URL,
            json=body.model_dump(mode="json"),
            token=token
        )

        status_result = response.get("status")

        if status_result >= 400:
            raise HTTPException(
                status_code=status_result,
                detail=response.get("data") or "Error al crear cliente"
            )

        return {
            "message": "Cliente creado exitosamente",
            "data": response
        }

    except HTTPException as e:
        status_result = e.status_code
        raise e

    except Exception as e:
        status_result = 500
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        await operations_service.log(
            accion="ACTUALIZAR",
            usuario=None,
            cliente_id=body.usuarioId,
            resultado=str(status_result)
        )


@router.get(
    "/obtener/{user_id}",
    summary="Obtener cliente por ID",
    description="""
Recupera los datos completos de un cliente específico usando su ID.

**Flujo:**
1. Valida que el header `Authorization` esté presente.
2. Extrae el Bearer token.
3. Realiza un GET al servicio externo en `OBTENER_CLIENTE_URL/{user_id}`.
4. Si la respuesta está vacía o es falsy, retorna HTTP 404.
5. Retorna los datos del cliente directamente.

**Path parameter:**
- `user_id`: ID único del cliente a consultar.

**Header requerido:**
```
Authorization: Bearer <token>
```
    """,
    responses={
        200: {
            "description": "Datos del cliente retornados exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "clienteId": "abc123",
                        "nombre": "Juan",
                        "apellidos": "Pérez",
                        "identificacion": "12345678"
                    }
                }
            }
        },
        401: {
            "description": "Token ausente.",
            "content": {"application/json": {"example": {"detail": "Token requerido"}}}
        },
        404: {
            "description": "Cliente no encontrado.",
            "content": {"application/json": {"example": {"detail": "Usuario no encontrado"}}}
        },
        500: {"description": "Error interno inesperado."},
    }
)
async def get_one_client(
    user_id: str,
    authorization: str = Header(None)
):
    operations_service = OperationsService()
    status_result = None

    try:
        if not authorization or not authorization.strip():
            status_result = 401
            raise HTTPException(status_code=401, detail="Token requerido")

        token = authorization.replace("Bearer ", "").strip()

        response = await http_client.get(f"{OBTENER_CLIENTE_URL}/{user_id}", token=token)

        if not response:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return response

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/eliminar/{user_id}",
    summary="Eliminar cliente",
    description="""
Elimina un cliente del sistema por su ID.

**Flujo:**
1. Valida que el header `Authorization` esté presente.
2. Extrae el Bearer token.
3. Llama al servicio externo (`ELIMINAR_CLIENTE_URL/{user_id}`) con método DELETE.
4. Si el servicio externo retorna un status >= 400, lanza la excepción con ese mismo status code.
5. Registra la operación en MongoDB (colección `operaciones`) con acción `ELIMINAR`, siempre en el bloque `finally`.
6. Retorna confirmación de eliminación.

**Path parameter:**
- `user_id`: ID único del cliente a eliminar.

**Notas:**
- La operación de auditoría siempre se registra, incluso si la eliminación falla.
- `usuario` se registra como `None` en la auditoría (no se recibe usuarioId en este endpoint).

**Header requerido:**
```
Authorization: Bearer <token>
```
    """,
    responses={
        200: {
            "description": "Cliente eliminado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Cliente eliminado correctamente",
                        "data": None
                    }
                }
            }
        },
        401: {
            "description": "Token ausente.",
            "content": {"application/json": {"example": {"detail": "Token requerido"}}}
        },
        400: {"description": "Error retornado por el servicio externo al intentar eliminar."},
        500: {"description": "Error interno inesperado."},
    }
)
async def delete_client(
    user_id: str,
    authorization: str = Header(None)
):
    operations_service = OperationsService()
    status_result = None

    try:
        if not authorization or not authorization.strip():
            status_result = 401
            raise HTTPException(status_code=401, detail="Token requerido")

        token = authorization.replace("Bearer ", "").strip()

        response = await http_client.delete(
            f"{ELIMINAR_CLIENTE_URL}/{user_id}",
            token=token
        )

        status_result = response.get("status")

        if status_result >= 400:
            raise HTTPException(
                status_code=status_result,
                detail=response.get("error") or response.get("text") or "Error al eliminar"
            )

        return {
            "message": "Cliente eliminado correctamente",
            "data": response.get("data")
        }

    except HTTPException as e:
        status_result = e.status_code
        raise e

    except Exception as e:
        status_result = 500
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        await operations_service.log(
            accion="ELIMINAR",
            usuario=None,
            cliente_id=user_id,
            resultado=str(status_result)
        )
