from fastapi import APIRouter, HTTPException

from services.api_usage import api_usage_counter
from util.logger import log_print
from util.nowtime import TaiwanTime

router = APIRouter(tags=["API Usage"])


@router.post("/ApiUsage/Upload")
@log_print
def upload_api_usage():
    """
    將本地 API 使用次數與 Firebase 歷史資料合併後上傳。
    """
    try:
        data = api_usage_counter.upload_usage()
        return {
            "status": "success",
            "localUploaded": data["local_uploaded"],
            "mergedDates": data["merged_dates"],
            "mergedUsage": data["merged_usage"],
            "updateTime": TaiwanTime.string(),
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
