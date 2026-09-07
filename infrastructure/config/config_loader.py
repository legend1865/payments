import os

from infrastructure.config.config_storage import Config

from dotenv import load_dotenv


def load_config_from_env() -> Config:
    load_dotenv()

    return Config(
        API_KEY=os.environ["API_KEY"],
        DATABASE_URL=os.environ["DATABASE_URL"],
        RABBITMQ_URL=os.environ["RABBITMQ_URL"],
        OUTBOX_POLL_INTERVAL=float(os.environ.get("OUTBOX_POLL_INTERVAL", "1")),
        OUTBOX_BATCH_SIZE=int(os.environ.get("OUTBOX_BATCH_SIZE", "100")),
        WEBHOOK_TIMEOUT=float(os.environ.get("WEBHOOK_TIMEOUT", "10")),
    )
