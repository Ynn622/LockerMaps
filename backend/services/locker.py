import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
from collections import defaultdict, OrderedDict
import re
import copy

from util.config import *

def getMRTLockerData():
    """
    爬取 台北捷運 置物櫃資料
    並轉成 JSON 格式。
    """
    url = "https://opendata.vip/metro/locker/station"
    web = requests.get(url)
    bs_web = bs(web.text, "html.parser")
    table = bs_web.find_all("div", class_="lk-card lk-avail")

    lis = []
    for card in table:
      data = {
          "name": card.get("data-name").replace("(BR12)",""),
          "line": card.get("data-line"),
          "desc": card.get("data-desc"),
          "available": int(card.get("data-avail")),
          "total": int(card.get("data-total")),
          "status": card.select_one(".lk-card-badge").get_text(strip=True),
          "display_name": card.select_one(".lk-card-name").get_text(strip=True),
          "availability_text": card.select_one(".lk-card-avail").get_text(" ", strip=True),
          "percentage": float(card.select_one(".lk-bar-fill").get("data-pct")),
          "meta": [
              tag.get_text(strip=True)
              for tag in card.select(".lk-card-meta .lk-meta-tag")
          ],
      }
      lis.append({
          "station": data["name"],
          "type": "MRT",
          "loc": data["desc"],
          "id": 0,
          "price": data["meta"][-1].replace("💰 ","") if data["meta"][-1].startswith("💰") else "20元/小時",
          "size": "S" if ("10元" in data["meta"][-1]) else "L",
          "empty": data["available"],
          "total": data["total"],
      })
    df = pd.DataFrame(lis)

    # 分組整理
    result_json = []
    for (station, locker_type), g in df.groupby(["station", "type"]):
        result_json.append({
            "station": station,
            "type": locker_type,
            "tag": MRT_Mapping.get(station, []),
            "details": g.drop(columns=["station", "type"]).to_dict(orient="records")
        })

    return result_json

def getTRALockerData():
  """
    爬取 台鐵 置物櫃資料（北部10站)
    並轉成 JSON 格式。
  """
  url = "https://lockerinfo.autosale.com.tw/lockerDatas"
  web_json = requests.get(url).json()

  # 初始化輸出資料結構
  result = defaultdict(lambda: {"station": "", "type": "TRA", "tag": [], "details": []})
  # 整理資料
  for item in web_json:
      key = item["lockerKey"]
      detail = json.loads(item["lockerDetail"])
      l_empty = detail["l"]["empty"]
      s_empty = detail["s"]["empty"]

      if key in locker_map:
          station, loc = locker_map[key]
          result[station]["station"] = station
          result[station]["details"].append({
              "loc": f"{station} {loc}",
              "id": key,
              "price": "60~90元/3小時",
              "size": "L",
              "total": None,
              "empty": l_empty,
          })
          result[station]["details"].append({
              "loc": f"{station} {loc}",
              "id": key,
              "price": "30~50元/3小時",
              "size": "S",
              "total": None,
              "empty": s_empty,
          })
      else:
          print(f"⚠️ 找不到對應 lockerKey: {key}")

  # 轉成 list 輸出
  output = list(result.values())

  # 印出結果（格式化 JSON）
  return output

def getOWLockerData():
  """
    爬取 OWLocker 置物櫃資料
    並轉成 JSON 格式。
  """
  url = "https://owlocker.com/api/info"
  web_json = requests.get(url).json()
  result = []
  for item in web_json:
    station = item['co_unit_i18n']['zh-TW'].strip()
    for site in item['sites']:
        detail = []
        for locker in site['lockers_type']:
            size = { 'L': 'L', 'M': 'S', 'S': '手機充電'}
            price =  {'L': '60元/3小時', 'M': '40元/3小時', 'S': '30元/3小時'}
            detail.append({
                'loc': re.sub(r"^[\d\s~]+", "", site['site_i18n']['zh-TW']).replace("  ( ","(").replace(" ( ","(").replace(" )",")"),
                'id': int(site['site_no']),
                'price': price.get(locker['size'], None),
                'size': size.get(locker['size'], None),
                'total': locker['total'],
                'empty': locker['empty']
            })
        # 更換 station
        tag = []
        loc = station
        if station in rules:
          tag.append(rules[station]['tag'])
          loc = rules[station]['loc'](detail[0]['loc'])

        result.append({
            'station': loc,
            'type': "OWL",
            'tag': tag,
            'details': detail,
        })
  return merge_station_details(result)

def getArenaLockerData():
    """
    爬取 台北小巨蛋 置物櫃資料
    並轉成 JSON 格式。
    """
    url = "https://web.metro.taipei/apis/metrostationapi/lockersinfoforrb"
    body = {"Field": "arena", "Lang": "TW"}
    web_json = requests.post(url, json=body).json()
    
    details = []
    for location in web_json:
        loc = location["PositionTW"].replace(" *供冰上樂園入場遊客使用", "")
        for closet in location["ClosetInfoList"]:
            # 計算價格
            hour_fee = int(closet["HourFee"])
            day_fee = int(closet["DayFee"])
            one_time_fee = int(closet["OneTimeFee"])
            
            if one_time_fee > 0:
                price = f"{one_time_fee}元/次"
            elif day_fee > 0:
                price = f"{day_fee}元/日"
            elif hour_fee > 0:
                price = f"{hour_fee}元/小時"
            else:
                price = "Unknown"
            
            # 尺寸映射：T4是中型，M是大型，其他小型
            size_code = closet["Size"]
            if size_code == "T4":
                size = "M"  # 中型
            elif closet["SizeField"] == "M":
                size = "L"  # 大型
            else:
                size = "S"  # 小型 (T1, T2 等)
            
            details.append({
                "loc": loc + " " + closet["SizeDescriptionTW"],
                "id": int(closet["ClosetID"]),
                "price": price,
                "size": size,
                "total": int(closet["Total"]),
                "empty": int(closet["Amount"])
            })
    
    result = [{
        "station": "台北小巨蛋",
        "type": "MRT",
        "tag": ["小巨蛋內"],
        "details": details
    }]
    
    return result

def getTcapLockerData():
    """
    爬取 兒童新樂園 置物櫃資料
    並轉成 JSON 格式。
    """
    url = "https://web.metro.taipei/apis/metrostationapi/lockersinfoforrb"
    body = {"Field": "tcap", "Lang": "TW"}
    web_json = requests.post(url, json=body).json()
    
    details = []
    for location in web_json:
        loc = location["PositionTW"]
        for closet in location["ClosetInfoList"]:
            # 計算價格
            hour_fee = int(closet["HourFee"])
            day_fee = int(closet["DayFee"])
            one_time_fee = int(closet["OneTimeFee"])
            
            if one_time_fee > 0:
                price = f"{one_time_fee}元/次"
            elif day_fee > 0:
                price = f"{day_fee}元/日"
            elif hour_fee > 0:
                price = f"{hour_fee}元/小時"
            else:
                price = "Unknown"
            
            # 尺寸映射：T4是大型，T3是中型，其他小型
            size_code = closet["Size"]
            if size_code == "T4":
                size = "L"  # 大型
            elif size_code == "T3":
                size = "M"  # 中型
            else:
                size = "S"  # 小型 (T1, T2 等)
            
            details.append({
                "loc": loc + " " + closet["SizeDescriptionTW"],
                "id": int(closet["ClosetID"]),
                "price": price,
                "size": size,
                "total": int(closet["Total"]),
                "empty": int(closet["Amount"])
            })
    
    result = [{
        "station": "兒童新樂園",
        "type": "MRT",
        "tag": ["兒童新樂園內"],
        "details": details
    }]
    
    return result

def merge_station_details(data):
    """
    將具有相同 'station' 名稱的 entries 合併，
    並將它們的 'details' 合併在一起。

    :param data: List of dicts (原始資料)
    :return: List of dicts (合併後資料)
    """
    merged = {}

    for entry in data:
        station = entry['station']

        if station not in merged:
            # 新的 station，就建立一個新 entry
            merged[station] = {
                'station': station,
                'type': entry['type'],
                'tag': copy.deepcopy(entry['tag']),
                'details': []
            }

        # 將 details 加入合併項中
        merged[station]['details'].extend(entry['details'])

    return list(merged.values())


def getKRTCLockerData():
    """
    回傳高雄捷運置物櫃資料（hardcode 版）。

    高雄捷運沒有公開即時空櫃資料，因此：
    - total：PDF 上的總櫃數
    - empty：None（無法得知即時空櫃數量）
    """
    grouped = OrderedDict()

    for station, locker_kind, loc, items in KRTC_LOCKERS:
        key = (station, "KRTC")
        grouped.setdefault(key, [])

        # 依照「位置 + 收費 + 大小(S/L)」合併，保留 size_detail 讓資料不失真。
        by_detail = defaultdict(lambda: {"total": 0, "size_codes": defaultdict(int)})
        for size_code, count, price in items:
            if size_code.startswith("S"):
                size = "S"
            elif size_code.startswith("M"):
                size = "M"
            else:
                size = "L"
            detail_key = (loc, price, size, locker_kind)
            by_detail[detail_key]["total"] += count
            by_detail[detail_key]["size_codes"][size_code] += count

        for detail_index, ((loc, price, size, locker_kind), data) in enumerate(by_detail.items(), start=1):
            total = data["total"]
            grouped[key].append({
                "loc": loc,
                "id": detail_index,
                "price": price,
                "size": size,
                "empty": None, # 無法得知即時空櫃數量
                "total": total,
                # 以下是高雄版額外保留的欄位；若前端沒用到，忽略即可。
                "locker_kind": locker_kind,
                "size_detail": ", ".join(
                    f"{code}:{num}" for code, num in sorted(data["size_codes"].items())
                ),
            })

    result_json = []
    for (station, locker_type), details in grouped.items():
        result_json.append({
            "station": station,
            "type": locker_type,
            "tag": KRTC_STATION_TAGS.get(station, []) + ["無即時資料"],
            "details": details,
        })

    return result_json


if __name__ == "__main__":
    with open("MRTLocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getMRTLockerData(), ensure_ascii=False, indent=2))
    with open("TRALocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getTRALockerData(), ensure_ascii=False, indent=2))
    with open("OWLocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getOWLockerData(), ensure_ascii=False, indent=2))
    with open("ArenaLocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getArenaLockerData(), ensure_ascii=False, indent=2))
    with open("TcapLocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getTcapLockerData(), ensure_ascii=False, indent=2))
