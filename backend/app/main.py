import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    last_error: Exception | None = None
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            last_error = None
            break
        except SQLAlchemyError as exc:
            last_error = exc
            await asyncio.sleep(2)

    if last_error is not None:
        raise last_error
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description='校园二手交易平台课程项目 API 框架',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'SecondHand backend is running'}


app.include_router(api_router, prefix='/api')

from app.api.my_task import router as my_task_router

app.include_router(my_task_router)