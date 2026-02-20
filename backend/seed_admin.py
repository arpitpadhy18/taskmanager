import asyncio
import os
import motor.motor_asyncio
from passlib.context import CryptContext
from datetime import datetime

# Direct config for script
MONGO_DETAILS = "mongodb://localhost:27017"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

async def create_admin():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    database = client.task_manager
    user_collection = database.get_collection("users")

    admin_email = "admin@taskmanager.com"
    admin_user = await user_collection.find_one({"email": admin_email})

    if not admin_user:
        admin_data = {
            "fullname": "Administrator",
            "email": admin_email,
            "password": get_hashed_password("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        await user_collection.insert_one(admin_data)
        print(f"✅ Admin user created successfully!")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Password: admin123")
    else:
        print("ℹ️ Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(create_admin())
