import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.db import init_db
from app.services.simulator import simulation_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    stop_event = asyncio.Event()
    task = None
    if os.getenv("LDS_TEST_MODE") != "1":
        task = asyncio.create_task(simulation_loop(stop_event))
        app.state.sim_stop_event = stop_event
        app.state.sim_task = task
    logger.info("LDS backend started")
    try:
        yield
    finally:
        if task is not None:
            stop_event.set()
            await task
        logger.info("LDS backend shutdown")


app = FastAPI(title="LDS Backend", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
