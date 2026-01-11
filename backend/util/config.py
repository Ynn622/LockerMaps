from geopy.geocoders import Nominatim
from firebase_admin import credentials, firestore
import firebase_admin
import re

from util.logger import Log, Color
from util.env import Env

class StationGPSManager:
    """
    站點 GPS 資料管理器（單例模式）
    
    功能：
    1. reload(): 從 Firebase 擷取所有站點資料並快取。
    2. get_or_create_gps(station_name): 取得或建立站點的 GPS 座標。
    3. upload(station_name, lat, lng): 上傳站點的 GPS 座標。
    4. get_station_GPS_dict(): 取得完整的 GPS 快取字典。
    5. 支援 len() 與 in 運算子。
    """
    from util.logger import Log, Color
    
    _instance = None
    _initialized = False
    searchedStation = []    # 已搜尋過的站點列表
    
    def __new__(cls, firebase_cred_path=Env.FIREBASE_SECRET):
        """單例模式：確保只有一個實例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, firebase_cred_path=Env.FIREBASE_SECRET):
        """初始化 GPS 管理器"""
        if not self._initialized:
            self._cache = {}
            self._db = None
            self._geolocator = Nominatim(user_agent="geoapi")
            
            # 初始化 Firebase
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(firebase_cred_path)
                    firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                
                # 首次建立時從 Firebase 載入資料
                self.reload()
                StationGPSManager._initialized = True
            except Exception as e:
                Log("Firebase 初始化失敗：", e, color=Color.RED)
                Log("使用空白快取字典", color=Color.YELLOW)
    
    def reload(self):
        """重新從 Firebase 擷取所有站點資料"""
        if self._db is None:
            Log("Firebase 未初始化", color=Color.RED)
            return
        
        try:
            Log("正在從 Firebase 載入站點資料...", color=Color.ORANGE)
            self._cache.clear()
            
            docs = self._db.collection('stations').stream()
            for doc in docs:
                data = doc.to_dict()
                # 使用原始站點名稱作為 key
                station_name = data.get('name', doc.id)
                self._cache[station_name] = data['data']
            
            Log(f"成功載入 {len(self._cache)} 個站點", color=Color.GREEN)
        except Exception as e:
            Log(f"載入失敗：{e}", color=Color.RED)
    
    def get_or_create_gps(self, station_name):
        """取得或建立站點的 GPS 座標
        Args:
            station_name: 站點名稱
        Returns:
            dict: {'lat': float, 'lng': float} 或 None（如果查詢失敗）
        """
        # 先檢查快取
        if station_name in self._cache:
            return self._cache[station_name]
        
        # 使用 Nominatim 查詢
        try:
            if station_name in self.searchedStation: return None    # 避免重複查詢
            Log(f"正在查詢 {station_name} 的 GPS 座標...", color=Color.ORANGE)
            location = self._geolocator.geocode(station_name + ", Taiwan")
            
            if location:
                gps_data = {
                    'lat': location.latitude,
                    'lng': location.longitude
                }
                
                # 存入快取
                self._cache[station_name] = gps_data
                # 回存 Firebase
                if self._db:
                    try:
                        clean_name = station_name.replace('/', '-')
                        doc_ref = self._db.collection('stations').document(clean_name)
                        doc_ref.set({
                            'name': station_name,
                            'data': gps_data
                        })
                        Log(f"已存入 Firebase：「{station_name} - {gps_data}」", color=Color.GREEN)
                    except Exception as e:
                        Log(f"存入 Firebase 失敗：{e}", color=Color.RED)
                return gps_data
            else:
                Log(f"找不到 {station_name} 的 GPS 座標", color=Color.YELLOW)
        except Exception as e:
            Log(f"查詢失敗：{e}", color=Color.RED)
        
        self.searchedStation.append(station_name)   # 記錄已搜尋過的站點
        return None

    def upload(self, station_name, lat, lng):
        """
        上傳站點的 GPS 座標
        Args:
            station_name: 站點名稱
            lat: 緯度
            lng: 經度
        """
        try:
            # 回存 Firebase
            if self._db:
                try:
                    clean_name = station_name.replace('/', '-')
                    doc_ref = self._db.collection('stations').document(clean_name)
                    gps_data = {'lat': lat, 'lng': lng}
                    doc_ref.set({
                        'name': station_name,
                        'data': gps_data
                    })
                    self._cache[station_name] = gps_data
                    Log(f"已存入 Firebase＆快取：「{station_name} - {gps_data}」", color=Color.GREEN)
                except Exception as e:
                    Log(f"存入 Firebase 失敗：{e}", color=Color.RED)
        except Exception as e:
            Log(f"新增失敗：{e}", color=Color.RED)
        
        self.searchedStation.append(station_name)   # 記錄已搜尋過的站點
    
    def get_station_GPS_dict(self):
        """
        取得完整的 GPS 快取字典
        Returns:
            dict: 所有站點的 GPS 資料
        """
        return self._cache.copy()
    
    def __len__(self):
        """回傳快取中的站點數量"""
        return len(self._cache)
    
    def __contains__(self, station_name):
        """支援 in 運算子：站點名稱 in manager"""
        return station_name in self._cache

StationGPSManager = StationGPSManager()

# lockerKey 對應的 車站與地點
locker_map = {
    91: ("基隆南站", "1樓廣場"),
    92: ("基隆南站", "1樓廣場"),
    94: ("七堵車站", "1樓"),
    97: ("南港車站", "B2"),
    98: ("南港車站", "B2"),
    292: ("南港車站", "B2"),
    293: ("南港車站", "B2"),
    294: ("南港車站", "B2"),
    37: ("松山車站", "B1"),
    38: ("松山車站", "B1"),
    39: ("松山車站", "B1"),
    2: ("台北車站", "B1 高鐵出口"),
    3: ("台北車站", "B1 高鐵出口"),
    4: ("台北車站", "B1 高鐵出口"),
    5: ("台北車站", "B1 高鐵出口"),
    6: ("台北車站", "B1 高鐵出口"),
    10: ("台北車站", "B1 南迴廊"),
    11: ("台北車站", "B1 南迴廊"),
    12: ("台北車站", "B1 南迴廊"),
    13: ("台北車站", "B1 南迴廊"),
    14: ("台北車站", "B1 南迴廊"),
    15: ("台北車站", "B1 南迴廊"),
    16: ("台北車站", "B1 東南區"),
    17: ("台北車站", "B1 東南區"),
    150: ("台北車站", "B1 東北角 淡水捷運方向"),
    151: ("台北車站", "B1 東北角 淡水捷運方向"),
    152: ("台北車站", "B1 東北角 淡水捷運方向"),
    153: ("台北車站", "B1 東北角 淡水捷運方向"),
    155: ("台北車站", "B1 東北角 淡水捷運方向"),
    159: ("台北車站", "B1 東北角 淡水捷運方向"),
    163: ("台北車站", "B1 北迴廊"),
    164: ("台北車站", "B1 北迴廊"),
    165: ("台北車站", "B1 北迴廊"),
    76: ("板橋車站", "1樓"),
    77: ("板橋車站", "1樓"),
    78: ("板橋車站", "1樓"),
    79: ("板橋車站", "B1"),
    80: ("板橋車站", "B1"),
    81: ("板橋車站", "B1"),
    82: ("板橋車站", "B1"),
    83: ("板橋車站", "B1"),
    84: ("板橋車站", "B1"),
    85: ("板橋車站", "B1"),
    139: ("板橋車站", "B1"),
    140: ("板橋車站", "B1"),
    74: ("樹林車站", "前站"),
    75: ("樹林車站", "前站"),
    31: ("桃園車站", "新站2樓"),
    32: ("桃園車站", "新站1樓"),
    33: ("桃園車站", "新站1樓"),
    24: ("中壢車站", "前站"),
    25: ("中壢車站", "前站"),
    18: ("新竹車站", "出口"),
    19: ("新竹車站", "出口"),
    20: ("新竹車站", "出口"),
    21: ("新竹車站", "出口"),
}

# 台北捷運站名對應代碼
MRT_Mapping = {
    # 轉乘站
    "板橋站": ["BL07", "Y16"],
    "新埔站": ["BL08", "Y17"],
    "西門站": ["BL11", "G12"],
    "台北車站": ["BL12", "R10"],
    "忠孝新生站": ["BL14", "O07"],
    "忠孝復興站": ["BL15", "BR10"],
    "南港展覽館": ["BL23", "BR24"],

    "大坪林站": ["G04", "Y07"],
    "古亭站": ["G09", "O05"],
    "中正紀念堂站": ["R08", "G10"],
    "中山站": ["R11", "G14"],
    "松江南京站": ["G15", "O08"],
    "南京復興站": ["BR11", "G16"],

    "景安站": ["O02", "Y11"],
    "東門站": ["R07", "O06"],
    "民權西路站": ["R13", "O11"],
    "頭前庄站": ["O17", "Y18"],
    "大安站": ["R05", "BR09"],

    # 文湖線（BR）
    "動物園站": ["BR01"],
    "木柵站": ["BR02"],
    "萬芳社區站": ["BR03"],
    "萬芳醫院站": ["BR04"],
    "辛亥站": ["BR05"],
    "麟光站": ["BR06"],
    "六張犁站": ["BR07"],
    "科技大樓站": ["BR08"],
    "中山國中站": ["BR12"],
    "松山機場站": ["BR13"],
    "大直站": ["BR14"],
    "劍南路站": ["BR15"],
    "西湖站": ["BR16"],
    "港墘站": ["BR17"],
    "文德站": ["BR18"],
    "內湖站": ["BR19"],
    "大湖公園站": ["BR20"],
    "葫洲站": ["BR21"],
    "東湖站": ["BR22"],
    "南港軟體園區站": ["BR23"],

    # 淡水信義線（R）
    "象山站": ["R02"],
    "台北101/世貿站": ["R03"],
    "信義安和站": ["R04"],
    "大安森林公園站": ["R06"],
    "台大醫院站": ["R09"],
    "雙連站": ["R12"],
    "圓山站": ["R14"],
    "劍潭站": ["R15"],
    "士林站": ["R16"],
    "芝山站": ["R17"],
    "明德站": ["R18"],
    "石牌站": ["R19"],
    "唭哩岸站": ["R20"],
    "奇岩站": ["R21"],
    "北投站": ["R22"],
    "新北投站": ["R22A"],  # 支線
    "復興崗站": ["R23"],
    "忠義站": ["R24"],
    "關渡站": ["R25"],
    "竹圍站": ["R26"],
    "紅樹林": ["R27"],
    "淡水站": ["R28"],

    # 松山新店線（G）
    "新店站": ["G01"],
    "新店區公所站": ["G02"],
    "七張站": ["G03"],
    "小碧潭站": ["G03A"],  # 支線
    "景美站": ["G05"],
    "萬隆站": ["G06"],
    "公館站": ["G07"],
    "台電大樓站": ["G08"],
    "小南門站": ["G11"],
    "北門站": ["G13"],
    "台北小巨蛋站": ["G17"],
    "南京三民站": ["G18"],
    "松山站": ["G19"],

    # 中和新蘆線（O）
    "南勢角站": ["O01"],
    "永安市場站": ["O03"],
    "頂溪站": ["O04"],
    "行天宮站": ["O09"],
    "中山國小站": ["O10"],
    "大橋頭站": ["O12"],
    "台北橋站": ["O13"],
    "菜寮站": ["O14"],
    "三重站": ["O15"],
    "先嗇宮站": ["O16"],
    "新莊站": ["O18"],
    "輔大站": ["O19"],
    "丹鳳站": ["O20"],
    "迴龍站": ["O21"],
    "三重國小站": ["O50"],
    "三和國中站": ["O51"],
    "徐匯中學站": ["O52"],
    "三民高中站": ["O53"],
    "蘆洲站": ["O54"],

    # 板南線（BL）
    "頂埔站": ["BL01"],
    "永寧站": ["BL02"],
    "土城站": ["BL03"],
    "海山站": ["BL04"],
    "亞東醫院站": ["BL05"],
    "府中站": ["BL06"],
    "江子翠站": ["BL09"],
    "龍山寺站": ["BL10"],
    "善導寺站": ["BL13"],
    "忠孝敦化站": ["BL16"],
    "國父紀念館站": ["BL17"],
    "市政府站": ["BL18"],
    "永春站": ["BL19"],
    "後山埤站": ["BL20"],
    "昆陽站": ["BL21"],
    "南港站": ["BL22"],

    # 環狀線（Y）
    "十四張站": ["Y08"],
    "秀朗橋站": ["Y09"],
    "景平站": ["Y10"],
    "中和站": ["Y12"],
    "橋和站": ["Y13"],
    "中原站": ["Y14"],
    "板新站": ["Y15"],
    "新埔民生站": ["Y17"],
    "幸福站": ["Y19"],
    "新北產業園區站": ["Y20"],
    
    # 貓空纜車
    "貓空纜車": ["貓空纜車"],
}

rules = {
    '台灣高鐵': {
        'tag': '台灣高鐵',
        'loc': lambda loc: re.split(r"[(-]", loc)[0].strip()
    },
    '台鐵公司': {
        'tag': '台鐵',
        'loc': lambda loc: re.split(r"[(]", loc)[0].strip()
    },
    '桃園捷運': {
        'tag': '桃園捷運',
        'loc': lambda loc: re.split(r"[(]", loc)[0].strip()
    },
    '誠品生活': {
        'tag': '誠品生活',
        'loc': lambda loc: re.split(r"[(]", loc)[0].strip()
    },
    '台中捷運': {
        'tag': '台中捷運',
        'loc': lambda loc: loc
    }
}
