import threading
from typing import Dict
from firebase_admin import firestore

from util.nowtime import TaiwanTime
from util.logger import Log, Color


class APIUsageCounter:
    """單例：記錄 API 使用次數（日期 -> 次數），並支援與 Firebase 合併。"""

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._lock = threading.Lock()
                    cls._instance._usage_by_date = {}  # 本地增量資料：{date: count}
        return cls._instance

    def increment(self) -> int:
        """每次 API 被呼叫時 +1，回傳當日最新次數。"""
        today = TaiwanTime.string(time=False)
        with self._lock:
            self._usage_by_date[today] = self._usage_by_date.get(today, 0) + 1
            return self._usage_by_date[today]

    def get_local_usage(self) -> Dict[str, int]:
        """取得目前本地尚未同步的 API 使用量（日期 -> 次數）。"""
        with self._lock:
            return dict(self._usage_by_date)

    def upload_usage(self) -> dict:
        """
        先抓取 Firebase 的歷史資料，再與本地資料合併後回寫。
        若日期重疊，次數相加。
        """
        with self._lock:
            local_snapshot = dict(self._usage_by_date)

        try:
            db = firestore.client()
            firebase_usage: Dict[str, int] = {}

            for doc in db.collection("api_usage_daily").stream():
                raw = doc.to_dict() or {}
                date = raw.get("date", doc.id)
                count = raw.get("count", 0)
                try:
                    firebase_usage[date] = int(count)
                except (TypeError, ValueError):
                    firebase_usage[date] = 0

            merged_usage: Dict[str, int] = dict(firebase_usage)
            for date, count in local_snapshot.items():
                merged_usage[date] = merged_usage.get(date, 0) + count

            batch = db.batch()
            now = TaiwanTime.now()
            for date, count in merged_usage.items():
                doc_ref = db.collection("api_usage_daily").document(date)
                batch.set(
                    doc_ref,
                    {
                        "date": date,
                        "count": count,
                        "updated_at": now,
                    },
                    merge=True,
                )
            batch.commit()

            # 只清掉這次快照裡已同步的增量，避免上傳期間新增的計數遺失
            with self._lock:
                for date, synced_count in local_snapshot.items():
                    current = self._usage_by_date.get(date, 0) - synced_count
                    if current > 0:
                        self._usage_by_date[date] = current
                    else:
                        self._usage_by_date.pop(date, None)

            Log(
                f"✅ API 使用量已合併上傳 | 本地日期數: {len(local_snapshot)} | Firebase總日期數: {len(merged_usage)}",
                color=Color.GREEN,
            )
            return {
                "local_uploaded": local_snapshot,
                "merged_usage": merged_usage,
                "merged_dates": len(merged_usage),
            }
        except Exception as e:
            Log(f"❌ API 使用量合併上傳失敗: {str(e)}", color=Color.RED)
            raise Exception(f"API 使用量合併上傳失敗: {str(e)}")

api_usage_counter = APIUsageCounter()
