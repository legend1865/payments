from typing import Protocol

from application.dto import Payment


class WebhookGateway(Protocol):
    async def send(self, payment: Payment) -> None: ...
