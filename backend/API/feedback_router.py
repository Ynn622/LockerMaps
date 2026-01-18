from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.feedback import FeedbackService
from util.logger import log_print

router = APIRouter(tags=["Feedback"])

# 定義請求資料模型
class FeedbackRequest(BaseModel):
    type: str  # suggestion, bug, data, other
    name: str
    email: Optional[str] = None
    content: str

# 定義回應資料模型
class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None

@router.post("/feedback", response_model=FeedbackResponse)
@log_print
def create_feedback(feedback: FeedbackRequest):
    """
    接收使用者意見回饋並存入 Firebase
    
    參數:
    - type: 回饋類型 (suggestion/bug/data/other)
    - name: 使用者暱稱
    - email: Email (選填)
    - content: 意見內容
    """
    try:
        # 驗證回饋類型
        valid_types = ["suggestion", "bug", "data", "other"]
        if feedback.type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"無效的回饋類型。允許的類型: {', '.join(valid_types)}"
            )
        
        # 驗證內容長度
        if len(feedback.content.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="意見內容至少需要5個字元"
            )
        
        # 呼叫服務層處理
        feedback_id = FeedbackService.create_feedback(
            feedback_type=feedback.type,
            name=feedback.name,
            email=feedback.email,
            content=feedback.content
        )
        
        return FeedbackResponse(
            success=True,
            message="感謝您的回饋！我們會盡快處理。",
            feedback_id=feedback_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"送出回饋時發生錯誤: {str(e)}"
        )

@router.get("/feedback/stats")
@log_print
def get_feedback_stats():
    """
    取得意見回饋統計資料
    """
    try:
        stats = FeedbackService.get_feedback_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得統計資料時發生錯誤: {str(e)}"
        )
