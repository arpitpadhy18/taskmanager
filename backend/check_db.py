import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")

async def check_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    database = client.task_manager
    user_collection = database.get_collection("users")
    
    users = await user_collection.find().to_list(100)
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"Email: {u.get('email')}, Role: {u.get('role')}")

if __name__ == "__main__":
    asyncio.run(check_db())
