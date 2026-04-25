import httpx
from typing import Optional

class HTTPClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    def _get_headers(self, token: Optional[str] = None):
        headers = {
            "Content-Type": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def get(
            self,
            url: str,
            params: dict | None = None,
            token: str | None = None
        ):
            try:
                headers = self._get_headers(token)

                response = await self.client.get(
                    url,
                    params=params,
                    headers=headers
                )

                try:
                    data = response.json()
                except Exception:
                    data = response.text

                if response.status_code >= 400:
                    return {
                        "status": response.status_code,
                        "error": data
                    }

                return {
                    "status": response.status_code,
                    "data": data
                }

            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }

    async def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | None = None,
        token: str | None = None
    ):
        headers = self._get_headers(token)

        response = await self.client.post(
            url,
            json=json if json is not None else None,
            data=data if json is None else None,
            headers=headers
        )

        response.raise_for_status()

        try:
            return {"status": response.status_code, "data": response.json()}
        except Exception:
            return {
                "status_code": response.status_code,
                "text": response.text
            }
            
    async def delete(
            self,
            url: str,
            params: dict | None = None,
            token: str | None = None
        ):
            headers = self._get_headers(token)

            response = await self.client.delete(
                url,
                params=params,
                headers=headers
            )

            response.raise_for_status()

            try:
                return {
                    "status": response.status_code,
                    "data": response.json()
                }
            except Exception:
                return {
                    "status": response.status_code,
                    "data": response.text
                }

    async def close(self):
        await self.client.aclose()

http_client = HTTPClient()