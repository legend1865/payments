from datetime import datetime
from uuid import UUID

from application.dto import OutboxMessage
from infrastructure.database.models import OutboxModel

from sqlalchemy import select, update
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

    async def get_unpublished(self, limit: int) -> list[OutboxMessage]:
        statement = (
            select(OutboxModel)
            .where(OutboxModel.published_at.is_(None))
            .order_by(OutboxModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        models = (await self._session.scalars(statement)).all()
        return [self._to_dto(model) for model in models]

    async def mark_as_published(self, message_id: UUID, published_at: datetime) -> None:
        statement = update(OutboxModel).where(OutboxModel.id == message_id).values(published_at=published_at)
        await self._session.execute(statement)

    @staticmethod
    def _to_dto(model: OutboxModel) -> OutboxMessage:
        return OutboxMessage(
            id=model.id,
            event_name=model.event_name,
            payload=model.payload,
            created_at=model.created_at,
            published_at=model.published_at,
        )
