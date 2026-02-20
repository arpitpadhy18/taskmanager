from fastapi import APIRouter, Body, HTTPException, status, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from bson import ObjectId

from database import user_collection, task_collection
from models import UserSchema, UserLoginSchema
from auth import get_hashed_password, verify_password, create_access_token, get_admin_user
from emails import send_credentials_email

router = APIRouter()

@router.post("/register", response_description="Add new user")
async def register_user(
    background_tasks: BackgroundTasks,
    user: UserSchema = Body(...), 
    admin: dict = Depends(get_admin_user)
):
    # Check if user already exists
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Store plain password for email before hashing
    plain_password = user.password
    
    # Hash password and save user
    user.password = get_hashed_password(user.password)
    user_dict = jsonable_encoder(user)
    user_dict["created_at"] = datetime.utcnow()
    
    await user_collection.insert_one(user_dict)
    
    # Send email in background
    background_tasks.add_task(
        send_credentials_email, 
        user.email, 
        user.fullname, 
        plain_password
    )
    
    return {"message": "User registered successfully and credentials sent to email"}

@router.get("/users", response_description="Get all users")
async def get_all_users(admin: dict = Depends(get_admin_user)):
    users = []
    async for user in user_collection.find():
        users.append({
            "id": str(user["_id"]),
            "fullname": user["fullname"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "created_at": user.get("created_at", "").isoformat() if user.get("created_at") else None
        })
    return users

@router.post("/login", response_description="Login user")
async def login_user(user: UserLoginSchema = Body(...)):
    user_data = await user_collection.find_one({"email": user.email})
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    if not verify_password(user.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": create_access_token(user_data["email"]),
        "token_type": "bearer",
        "user_id": str(user_data["_id"]),
        "email": user_data["email"],
        "fullname": user_data["fullname"],
        "role": user_data.get("role", "user")
    }

@router.delete("/users/{user_id}", response_description="Delete a user")
async def delete_user(user_id: str, admin: dict = Depends(get_admin_user)):
    # Check if user exists
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if str(admin["_id"]) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    # Check if user has assigned tasks
    tasks_count = await task_collection.count_documents({"assigned_to": user_id})
    if tasks_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete user. They have {tasks_count} assigned task(s). Please reassign or delete their tasks first."
        )
    
    # Delete the user
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete user"
    )
