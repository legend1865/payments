import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from presentation.http_api.endpoints import router

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    provided_api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    expected_api_key = os.getenv("API_KEY")
    if expected_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key is not configured",
        )
    if provided_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Infrastructure resources will be initialized here on the database step.
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Payments processing service",
        version="1.0.0",
        lifespan=lifespan,
        dependencies=[Depends(verify_api_key)],
    )
    app.include_router(router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("presentation.http_api.main:app", host="0.0.0.0", port=8000, reload=True)
