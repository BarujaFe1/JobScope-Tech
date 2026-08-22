"""JobScope Tech BR API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.pipeline import run_pipeline


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    init_db()
    if settings.jobscope_demo_mode:
        db = SessionLocal()
        try:
            from sqlalchemy import func, select

            from app.models import Job

            count = db.scalar(select(func.count(Job.id))) or 0
            if count == 0:
                run_pipeline(db)
        finally:
            db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="JobScope Tech BR API",
        description="API mínima para explorar vagas tech normalizadas no Brasil.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
