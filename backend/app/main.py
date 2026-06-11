import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.migrations import run_legacy_mysql_migrations
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    last_error: Exception | None = None
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            run_legacy_mysql_migrations(engine)
            last_error = None
            break
        except SQLAlchemyError as exc:
            last_error = exc
            await asyncio.sleep(2)

    if last_error is not None:
        if isinstance(last_error, OperationalError):
            raise RuntimeError(
                '无法连接到 MySQL 数据库。请先启动数据库服务，例如在项目根目录执行 '
                '`docker compose up -d mysql`，并确认 backend/.env 中的 DATABASE_URL '
                '与 README 中的 127.0.0.1:3307 配置一致。'
            ) from last_error
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
