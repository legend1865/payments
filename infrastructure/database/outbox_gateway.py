from application.dto import OutboxMessage
from infrastructure.database.models import OutboxModel

from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyOutboxGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, message: OutboxMessage) -> None:
        self._session.add(
            OutboxModel(
                id=message.id,
                event_name=message.event_name,
                payload=message.payload,
                created_at=message.created_at,
                published_at=message.published_at,
            )
        )
