import asyncio
import motor.motor_asyncio

async def check_db():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    database = client.task_manager
    user_collection = database.get_collection("users")
    
    users = await user_collection.find().to_list(100)
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"Email: {u.get('email')}, Role: {u.get('role')}")

if __name__ == "__main__":
    asyncio.run(check_db())
