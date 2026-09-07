from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Config:
    API_KEY: str
    DATABASE_URL: str
    RABBITMQ_URL: str
    OUTBOX_POLL_INTERVAL: float
    OUTBOX_BATCH_SIZE: int
    WEBHOOK_TIMEOUT: float

    SUCCESS_PROBABILITY: Final[float] = 0.9
    PAYMENT_PROCESSING_MIN_DELAY: Final[float] = 2.0
    PAYMENT_PROCESSING_MAX_DELAY: Final[float] = 5.0
    MAX_ATTEMPTS: Final[int] = 3
    RETRY_COUNT_HEADER: Final[str] = "x-retry-count"
    ERROR_TYPE_HEADER: Final[str] = "x-error-type"
