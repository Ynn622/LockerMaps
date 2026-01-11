import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
from collections import defaultdict
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
    table = bs_web.find("table", class_="myDataTable").find("tbody").find_all("tr")

    lis = []
    for tr in table[1:]:
        rowData = [s.text.replace(" ","").replace("\n","").replace("尚有空間","").replace("已滿","").replace("(BR12)","") for s in tr.find_all("td")]
        station, loc, price = rowData[:3]
        price = "20元/小時" if price == "-" else price
        size = "S" if ("10元" in rowData[2]) else "L"
        empty, total = rowData[3].split("/")
        lis.append({
            "station": station,
            "type": "MRT",
            "loc": loc.replace("近", ""),
            "id": 0,
            "price": price,
            "size": size,
            "empty": int(empty),
            "total": int(total),
        })
    df = pd.DataFrame(lis)

    # 分組整理
    result_json = df.groupby(["station", "type"], group_keys=False).apply(
        lambda g: {
            "station": g.name[0],
            "type": g.name[1],
            "tag": MRT_Mapping.get(g.name[0], []),
            "details": g.to_dict(orient="records")
        }, include_groups=False
    ).tolist()

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

if __name__ == "__main__":
    with open("MRTLocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getMRTLockerData(), ensure_ascii=False, indent=2))
    with open("TRALocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getTRALockerData(), ensure_ascii=False, indent=2))
    with open("OWLocker.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(getOWLockerData(), ensure_ascii=False, indent=2))
