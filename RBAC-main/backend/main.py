from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.bootstrap import init_db
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await init_db(session)
    yield

from app.core.exceptions import APIException, custom_http_exception_handler
app = FastAPI(title="RBAC System API", lifespan=lifespan)
app.add_exception_handler(APIException, custom_http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")