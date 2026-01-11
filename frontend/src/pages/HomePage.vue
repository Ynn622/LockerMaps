<template>
    <div class="flex flex-col w-full h-[100dvh]">
        <!-- 頂部標題列 -->
        <div class="bg-gray-100 shadow-md">
            <div class="px-4 py-2 flex items-center gap-3">
                <i class="fa-solid fa-map-location-dot text-3xl"></i>
                <span class="flex flex-col">
                    <span class="text-xl text-gray-800 font-bold">LockerMaps</span>
                    <p class="text-xs text-gray-600">台灣置物櫃速查</p>
                </span>
            </div>
        </div>

        <!-- Mapbox 地圖容器 -->
        <div ref="mapContainer" class="flex-1 w-full h-full"></div>

        <!-- 詳細資訊面板 -->
        <DetailPanel ref="detailPanel" />
        
        <!-- 載入畫面 -->
        <Loading ref="loadingRef" />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import DetailPanel from './components/DetailPanel.vue';
import Loading from './components/Loading.vue';
import { getLockerData, type StationData } from '../utilities/lockerApi';
import { logger } from '../utilities/logger';
import { getMarkerColor } from '../utilities/colorUtils';

const mapContainer = ref<HTMLDivElement | null>(null);
const detailPanel = ref<InstanceType<typeof DetailPanel> | null>(null);
const loadingRef = ref<InstanceType<typeof Loading> | null>(null);
let map: mapboxgl.Map | null = null;
const markers: any = ref([]);
const lockerStations = ref<StationData[]>([]);

// Mapbox Access Token
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN as string;

// 載入置物櫃資料
const loadLockerData = async () => {
    try {
        loadingRef.value?.show('載入置物櫃資料中');
        logger.func.start('loadLockerData', []);
        const data = await getLockerData();
        lockerStations.value = data;
        logger.func.success('loadLockerData', []);
        logger.info('載入置物櫃資料成功，共', data.length, '個站點');
        
        // 添加標記點到地圖
        addMarkersToMap();
    } catch (error) {
        logger.func.error('loadLockerData', []);
        logger.error('載入置物櫃資料失敗:', error);
    } finally {
        // 隱藏 loading
        loadingRef.value?.hide();
    }
};

// 添加標記點到地圖
const addMarkersToMap = () => {
    if (!map) return;
    
    // 清除舊標記
    markers.value.forEach((marker: mapboxgl.Marker) => marker.remove());
    markers.value = [];
    
    // 添加新標記
    lockerStations.value.forEach(station => {
        if (!station.lat || !station.lng) return;
        
        // 創建標記（使用預設樣式，依類型設定顏色）
        const marker = new mapboxgl.Marker({ 
            color: getMarkerColor(station.type)
        })
            .setLngLat([station.lng, station.lat])
            .addTo(map!);
        
        // 點擊事件 - 顯示詳細資訊
        marker.getElement().addEventListener('click', () => {
            logger.info('點擊站點:', station.station);
            detailPanel.value?.show(station);
        });
        
        // 添加 hover 樣式
        marker.getElement().style.cursor = 'pointer';
        
        markers.value.push(marker);
    });
    
    logger.info('已添加', markers.value.length, '個標記點');
};

// 初始化地圖
const initMap = () => {
    if (!mapContainer.value) return;
    
    mapboxgl.accessToken = MAPBOX_TOKEN;
    
    map = new mapboxgl.Map({
        container: mapContainer.value,
        style: 'mapbox://styles/mapbox/streets-v12', // 淺色街道地圖
        center: [120.9605, 23.6978], // 台灣中心座標
        zoom: 7.5,
        pitch: 0, // 平面視角
        bearing: 0,
        interactive: true,
    });
    
    // 添加導航控制器
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    
    // 添加全螢幕控制器
    map.addControl(new mapboxgl.FullscreenControl(), 'top-right');
    
    // 添加比例尺
    map.addControl(new mapboxgl.ScaleControl({
        maxWidth: 100,
        unit: 'metric'
    }), 'bottom-left');
    
    // 地圖載入完成事件
    map.on('load', () => {
        logger.info('地圖載入完成');
        
        // 設置地圖顯示語言為中文
        const layers = map?.getStyle().layers ?? []

        for (const layer of layers) {
            if (layer.type !== 'symbol') continue
            if (!layer.id.includes('label')) continue  // ✅ 只改 label 類

            const tf = (layer.layout as any)?.['text-field']
            if (!tf) continue

            map?.setLayoutProperty(layer.id, 'text-field', [
                'coalesce',
                ['get', 'name_zh-Hant'],
                ['get', 'name']
            ])
        }
        
        // 載入置物櫃資料
        loadLockerData();
    });
};

onMounted(() => {
    initMap();
});

onUnmounted(() => {
    // 清除標記
    markers.value.forEach((marker: mapboxgl.Marker) => marker.remove());
    markers.value = [];
    
    map?.remove();
    map = null;
});

// 導出 map 實例供外部使用
defineExpose({
    map
});
</script>