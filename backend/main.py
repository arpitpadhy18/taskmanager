from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as AuthRouter
from routes.tasks import router as TaskRouter

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")
app.include_router(TaskRouter, tags=["Tasks"], prefix="/tasks")

@app.get("/")
async def root():
    return {"message": "Welcome to the Task Manager API"}
