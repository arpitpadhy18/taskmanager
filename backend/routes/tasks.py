from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from bson import ObjectId

from database import task_collection, user_collection
from models import TaskSchema, TaskUpdateSchema
from auth import get_current_user, get_admin_user

router = APIRouter()

@router.post("/", response_description="Create new task")
async def create_task(task: TaskSchema = Body(...), admin: dict = Depends(get_admin_user)):
    # Verify assigned user exists
    user = await user_collection.find_one({"_id": ObjectId(task.assigned_to)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    task_dict = jsonable_encoder(task)
    task_dict["created_at"] = datetime.utcnow()
    task_dict["created_by"] = str(admin["_id"])
    
    result = await task_collection.insert_one(task_dict)
    
    return {
        "message": "Task created successfully",
        "task_id": str(result.inserted_id)
    }

@router.get("/", response_description="Get all tasks")
async def get_all_tasks(admin: dict = Depends(get_admin_user)):
    tasks = []
    async for task in task_collection.find():
        # Get assigned user info
        user = await user_collection.find_one({"_id": ObjectId(task["assigned_to"])})
        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "assigned_to": {
                "id": task["assigned_to"],
                "fullname": user["fullname"] if user else "Unknown",
                "email": user["email"] if user else "Unknown"
            },
            "due_date": task["due_date"],
            "status": task.get("status", "pending"),
            "priority": task.get("priority", "medium"),
            "created_at": task.get("created_at", "").isoformat() if task.get("created_at") else None
        })
    return tasks

@router.get("/my", response_description="Get my tasks")
async def get_my_tasks(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    tasks = []
    async for task in task_collection.find({"assigned_to": user_id}):
        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "due_date": task["due_date"],
            "status": task.get("status", "pending"),
            "priority": task.get("priority", "medium"),
            "created_at": task.get("created_at", "").isoformat() if task.get("created_at") else None
        })
    return tasks

@router.get("/stats", response_description="Get dashboard statistics")
async def get_dashboard_stats(admin: dict = Depends(get_admin_user)):
    # Count total users (excluding admins)
    total_users = await user_collection.count_documents({"role": {"$ne": "admin"}})
    
    # Count completed tasks
    completed_tasks = await task_collection.count_documents({"status": "completed"})
    
    # Count active tasks (pending + in_progress)
    active_tasks = await task_collection.count_documents({"status": {"$in": ["pending", "in_progress"]}})
    
    return {
        "total_users": total_users,
        "completed_tasks": completed_tasks,
        "active_tasks": active_tasks
    }

@router.get("/completed", response_description="Get all completed tasks")
async def get_completed_tasks(admin: dict = Depends(get_admin_user)):
    tasks = []
    async for task in task_collection.find({"status": "completed"}):
        user = await user_collection.find_one({"_id": ObjectId(task["assigned_to"])})
        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "assigned_to": {
                "id": task["assigned_to"],
                "fullname": user["fullname"] if user else "Unknown",
                "email": user["email"] if user else "Unknown"
            },
            "due_date": task["due_date"],
            "status": task.get("status", "completed"),
            "priority": task.get("priority", "medium"),
            "created_at": task.get("created_at", "").isoformat() if task.get("created_at") else None,
            "updated_at": task.get("updated_at", "").isoformat() if task.get("updated_at") else None
        })
    return tasks

@router.get("/active", response_description="Get all active tasks")
async def get_active_tasks(admin: dict = Depends(get_admin_user)):
    tasks = []
    async for task in task_collection.find({"status": {"$in": ["pending", "in_progress"]}}):
        user = await user_collection.find_one({"_id": ObjectId(task["assigned_to"])})
        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "assigned_to": {
                "id": task["assigned_to"],
                "fullname": user["fullname"] if user else "Unknown",
                "email": user["email"] if user else "Unknown"
            },
            "due_date": task["due_date"],
            "status": task.get("status", "pending"),
            "priority": task.get("priority", "medium"),
            "created_at": task.get("created_at", "").isoformat() if task.get("created_at") else None
        })
    return tasks

@router.put("/{task_id}/status", response_description="Update task status")
async def update_task_status(
    task_id: str, 
    task_update: TaskUpdateSchema = Body(...), 
    current_user: dict = Depends(get_current_user)
):
    # Find the task
    task = await task_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user is assigned to this task or is admin
    user_id = str(current_user["_id"])
    if task["assigned_to"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update status
    valid_statuses = ["pending", "in_progress", "completed"]
    if task_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    await task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": task_update.status, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Task status updated successfully"}
