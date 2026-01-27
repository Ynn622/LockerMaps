from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
import time
import threading

from services.locker import *
from util.logger import log_print, Log, Color
from util.config import StationGPSManager
from util.nowtime import TaiwanTime

router = APIRouter(tags=["LockerMaps Data"])

# 全域快取
cache_data = {}
last_fetch_time = 0
CACHE_TTL = 30  # 單位：秒
cache_lock = threading.Lock()  # 防止 race condition

@router.get("/Locker")
@log_print
def get_LockerData(type: str = Query(None, description="Locker type: MRT, TRA, OWL")):
    global cache_data, last_fetch_time
    try:
        now = time.time()
        
        # 超過 TTL 才重新爬
        if now - last_fetch_time > CACHE_TTL or not cache_data:
            with cache_lock:  # 使用鎖保護
                # 雙重檢查：進入鎖後再次確認是否需要更新
                if now - last_fetch_time > CACHE_TTL or not cache_data:
                    cache_data = {
                        "MRT": getMRTLockerData(),
                        "TRA": getTRALockerData(),
                        "OWL": getOWLockerData(),
                    }
                    last_fetch_time = time.time()  # 使用最新時間

        # 根據參數篩選
        if type in cache_data:
            data = cache_data[type]
        else:
            data = sum(cache_data.values(), []) # 合併所有類型
            for station in data:
                name = station["station"]
                stationData = StationGPSManager.get_station_GPS_dict()
                if name == "台北車站" and station["type"] == "TRA":
                    station.update({ "lat": 25.047784479915663, "lng": 121.51642612598873 })
                    continue
                if name in stationData:
                    station.update({
                        "lat": stationData[name]["lat"],
                        "lng": stationData[name]["lng"]
                    })
                else:
                    fetchData = StationGPSManager.get_or_create_gps(name)
                    station.update({
                        "lat": fetchData["lat"] if fetchData else 0,
                        "lng": fetchData["lng"] if fetchData else 0
                    })
        Log("資料更新時間：" ,datetime.fromtimestamp(last_fetch_time).strftime("%Y-%m-%d %H:%M:%S"), color=Color.GREEN, reload_only=True)
        return data
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@router.get("/ReloadStationGPS")
@log_print
def reload_station_gps():
    """
    強制重新載入所有站點的 GPS 資料。
    這會清空目前的快取並重新查詢所有站點的 GPS 座標。
    """
    try:
        StationGPSManager.reload()
        return {"status": "success", "updateTime": TaiwanTime.string()}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

class StationGPSUpdate(BaseModel):
    station: str
    lat: float
    lng: float

@router.post("/UpdateStationGPS")
@log_print
def update_station_gps(update: StationGPSUpdate):
    """
    更新指定站點的 GPS 座標。
    """
    try:
        StationGPSManager.upload(update.station, update.lat, update.lng)
        return {"status": "success", "updateTime": TaiwanTime.string()}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))