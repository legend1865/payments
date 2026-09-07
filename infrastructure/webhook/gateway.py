from application.dto import Payment

import httpx


class HttpxWebhookGateway:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def send(self, payment: Payment) -> None:
        response = await self._client.post(
            payment.webhook_url,
            json={
                "payment_id": str(payment.id),
                "status": payment.status.value,
                "processed_at": payment.processed_at.isoformat() if payment.processed_at is not None else None,
            },
        )
        response.raise_for_status()
