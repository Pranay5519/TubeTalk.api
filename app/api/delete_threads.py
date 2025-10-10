from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.utils.rag_utility import delete_all_threads_from_db
import sqlite3
import os

router = APIRouter(prefix="/del_threads", tags=["del_threads"])

@router.delete("/delete_all_threads")
async def delete_all_threads(input_value):
    """
    Endpoint to delete all threads from the database.
    """
    try:
        if input_value == "delete":
            delete_all_threads_from_db()
            return {"status": "✅ All threads deleted successfully."}
        else:
            return {"status" : "enter secret keywork to delete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error while deleting threads: {str(e)}")