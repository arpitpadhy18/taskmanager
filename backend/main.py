from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as AuthRouter
from routes.tasks import router as TaskRouter
from database import client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://taskmanager-liard-ten.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")
app.include_router(TaskRouter, tags=["Tasks"], prefix="/tasks")

@app.on_event("startup")
async def startup_db_client():
    try:
        # The ping command is cheap and does not require auth.
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")


@app.get("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Welcome to the Task Manager API"}
