from firebase_admin import firestore
from typing import Optional

from util.nowtime import TaiwanTime
from util.logger import Log, Color

class FeedbackService:
    """
    意見回饋服務層
    負責處理意見回饋的 Firebase 儲存與查詢
    """
    
    # 初始化 Firebase (StationGPSManager 已初始化)
    _db = None
    
    @classmethod
    def _get_db(cls):
        """取得 Firestore 資料庫實例"""
        if cls._db is None:
            cls._db = firestore.client()
        return cls._db
    
    @classmethod
    def create_feedback(
        cls,
        feedback_type: str,
        name: str,
        content: str,
        email: Optional[str] = None
    ) -> str:
        """
        建立新的意見回饋並存入 Firebase
        
        參數:
        - feedback_type: 回饋類型 (suggestion/bug/data/other)
        - name: 使用者暱稱
        - content: 意見內容
        - email: Email (選填)
        
        回傳:
        - feedback_id: Firebase 文件 ID
        """
        try:
            db = cls._get_db()
            
            # 準備回饋資料
            feedback_data = {
                "type": feedback_type,
                "name": name,
                "email": email if email else "",
                "content": content,
                "created_at": TaiwanTime.now(),
                "status": "pending",  # 狀態: pending, processing, resolved
                "resolved_at": None,
                "resolved_by": None,
                "notes": ""
            }
            
            # 存入 Firebase feedbacks 集合
            doc_ref = db.collection("feedbacks").add(feedback_data)
            feedback_id = doc_ref[1].id
            
            Log(f"✅ 意見回饋已建立 | ID: {feedback_id} | 類型: {feedback_type} | 提交者: {name}", color=Color.GREEN)
            
            return feedback_id
            
        except Exception as e:
            Log(f"❌ 建立意見回饋失敗: {str(e)}", color=Color.RED)
            raise Exception(f"建立意見回饋失敗: {str(e)}")
    
    @classmethod
    def get_feedback_stats(cls) -> dict:
        """
        取得意見回饋統計資料
        
        回傳:
        - dict: 包含各類型回饋的數量統計
        """
        try:
            db = cls._get_db()
            
            # 取得所有回饋
            feedbacks_ref = db.collection("feedbacks")
            feedbacks = feedbacks_ref.stream()
            
            stats = {
                "total": 0,
                "by_type": {
                    "suggestion": 0,
                    "bug": 0,
                    "data": 0,
                    "other": 0
                },
                "by_status": {
                    "pending": 0,
                    "processing": 0,
                    "resolved": 0
                }
            }
            
            for feedback in feedbacks:
                data = feedback.to_dict()
                stats["total"] += 1
                
                # 統計類型
                feedback_type = data.get("type", "other")
                if feedback_type in stats["by_type"]:
                    stats["by_type"][feedback_type] += 1
                
                # 統計狀態
                status = data.get("status", "pending")
                if status in stats["by_status"]:
                    stats["by_status"][status] += 1
            
            Log(f"📊 意見回饋統計 | 總數: {stats['total']}", color=Color.BLUE)
            
            return stats
            
        except Exception as e:
            Log(f"❌ 取得統計資料失敗: {str(e)}", color=Color.RED)
            raise Exception(f"取得統計資料失敗: {str(e)}")
    
    @classmethod
    def get_all_feedbacks(cls, limit: int = 100) -> list:
        """
        取得所有意見回饋 (管理用)
        
        參數:
        - limit: 最多回傳數量
        
        回傳:
        - list: 回饋清單
        """
        try:
            db = cls._get_db()
            
            feedbacks_ref = db.collection("feedbacks") \
                             .order_by("created_at", direction=firestore.Query.DESCENDING) \
                             .limit(limit)
            
            feedbacks = feedbacks_ref.stream()
            
            result = []
            for feedback in feedbacks:
                data = feedback.to_dict()
                data["id"] = feedback.id
                result.append(data)
            
            return result
            
        except Exception as e:
            Log(f"❌ 取得回饋清單失敗: {str(e)}", color=Color.RED)
            raise Exception(f"取得回饋清單失敗: {str(e)}")
    
    @classmethod
    def update_feedback_status(
        cls,
        feedback_id: str,
        status: str,
        resolved_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        更新意見回饋狀態 (管理用)
        
        參數:
        - feedback_id: 回饋 ID
        - status: 新狀態 (pending/processing/resolved)
        - resolved_by: 處理者
        - notes: 處理備註
        
        回傳:
        - bool: 是否更新成功
        """
        try:
            db = cls._get_db()
            
            update_data = {
                "status": status
            }
            
            if status == "resolved":
                update_data["resolved_at"] = TaiwanTime.now()
                if resolved_by:
                    update_data["resolved_by"] = resolved_by
            
            if notes:
                update_data["notes"] = notes
            
            db.collection("feedbacks").document(feedback_id).update(update_data)
            
            Log(f"✅ 意見回饋狀態已更新 | ID: {feedback_id} | 狀態: {status}", color=Color.GREEN)
            
            return True
            
        except Exception as e:
            Log(f"❌ 更新回饋狀態失敗: {str(e)}", color=Color.RED)
            raise Exception(f"更新回饋狀態失敗: {str(e)}")
