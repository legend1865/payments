from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from infrastructure.config import Config, load_config_from_env
from infrastructure.database import create_engine, create_session_factory
from presentation.http_api.endpoints import router

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    request: Request,
    provided_api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    expected_api_key = request.app.state.config.API_KEY
    if provided_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(app.state.config.DATABASE_URL)
    app.state.session_factory = create_session_factory(engine)
    try:
        yield
    finally:
        await engine.dispose()


def create_app(config: Config | None = None) -> FastAPI:
    app = FastAPI(
        title="Payments processing service",
        version="1.0.0",
        lifespan=lifespan,
        dependencies=[Depends(verify_api_key)],
    )
    app.state.config = config or load_config_from_env()
    app.include_router(router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("presentation.http_api.main:app", host="0.0.0.0", port=8000, reload=True)
