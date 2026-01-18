<template>
    <div class="flex flex-col w-full h-[100dvh]">
        <Nav flow="absolute"/>

        <!-- Mapbox 地圖容器 -->
        <div ref="mapContainer" class="flex-1 w-full h-full relative">
            <!-- 搜尋列 -->
            <SearchBar 
                :stations="lockerStations" 
                @select="handleStationSelect"
            />
            
            <!-- 重新載入按鈕 -->
            <button
                @click="reloadLockerData"
                :disabled="isReloading"
                class="absolute top-[185px] right-[8px] z-10 bg-white hover:bg-gray-100 text-gray-700 p-1.5 rounded shadow-md transition duration-200 border-gray-300/90 border-2 rounded-sm disabled:opacity-10 disabled:cursor-not-allowed"
                title="重新載入置物櫃資料中"
            >
                <i :class="['fa-solid fa-rotate-right text-sm', { 'animate-spin': isReloading }]"></i>
            </button>
        </div>

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
import { getLockerData, type StationData } from '../utilities/lockerApi';
import { logger } from '../utilities/logger';
import { getMarkerColor } from '../utilities/colorUtils';
import { useBreakpoints, breakpointsTailwind } from '@vueuse/core';

import DetailPanel from './components/DetailPanel.vue';
import Loading from './components/Loading.vue';
import SearchBar from './components/SearchBar.vue';
import Nav from './components/Nav.vue';
import { useToast } from '@/composables/useToast';

const mapContainer = ref<HTMLDivElement | null>(null);
const detailPanel = ref<InstanceType<typeof DetailPanel> | null>(null);
const loadingRef = ref<InstanceType<typeof Loading> | null>(null);
const toast = useToast();
let map: mapboxgl.Map | null = null;
const markers: any = ref([]);
const lockerStations = ref<StationData[]>([]);
const isReloading = ref(false);

// 響應式斷點偵測
const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller('md'); // < md

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

// 重新載入置物櫃資料
const reloadLockerData = async () => {
    if (isReloading.value) return;
    
    try {
        isReloading.value = true;
        logger.func.start('reloadLockerData', []);
        
        // 顯示載入提示
        loadingRef.value?.show('重新載入置物櫃資料中');
        
        // 重新獲取資料
        const data = await getLockerData();
        lockerStations.value = data;
        
        // 重新添加標記點
        addMarkersToMap();
        
        logger.func.success('reloadLockerData', []);
        logger.info('重新載入完成，共', data.length, '個站點');
        
        // 顯示成功提示
        toast?.show('資料已更新！', 'success', 3000);
    } catch (error) {
        logger.func.error('reloadLockerData', []);
        logger.error('重新載入失敗:', error);
        toast?.show('重新載入失敗，請稍後再試', 'error', 5000);
    } finally {
        isReloading.value = false;
        loadingRef.value?.hide();
    }
};

// 處理站點選擇（從搜尋列）
const handleStationSelect = (station: StationData) => {
    if (!map || !station.lat || !station.lng) return;
    
    logger.info('選擇站點:', station.station);
    
    // 飛到選擇的站點位置
    map.flyTo({
        center: [station.lng, station.lat-(isMobile.value ? 0.005 : 0)],
        zoom: 14,
        duration: 1500,
        essential: true
    });
    
    // 延遲一下再顯示詳細資訊，讓地圖飛行動畫更流暢
    setTimeout(() => {
        detailPanel.value?.show(station);
    }, 800);
};

// 初始化地圖
const initMap = () => {
    if (!mapContainer.value) return;
    
    mapboxgl.accessToken = MAPBOX_TOKEN;

    map = new mapboxgl.Map({
        container: mapContainer.value,
        style: 'mapbox://styles/mapbox/streets-v12', // 淺色街道地圖
        center: [120.9605, 23.6978], // 台灣中心座標
        zoom: isMobile.value ? 6.5 : 7,
        pitch: 0, // 平面視角
        bearing: 0,
        interactive: true,
    });
    
    // 添加導航控制器
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    
    // 添加全螢幕控制器
    map.addControl(new mapboxgl.FullscreenControl(), 'top-right');
    
    // 添加定位控制器
    const geolocateControl = new mapboxgl.GeolocateControl({
        positionOptions: {
            enableHighAccuracy: true // 使用高精度定位
        },
        trackUserLocation: true, // 持續追蹤使用者位置
        showUserHeading: true, // 顯示使用者方向
        showUserLocation: true, // 顯示使用者位置
        showAccuracyCircle: true // 顯示精度範圍圓圈
    });
    map.addControl(geolocateControl, 'top-right');
    
    // 監聽定位錯誤事件
    geolocateControl.on('error', (error) => {
        logger.error('定位錯誤:', error);
        let toastMessage = '';
        
        if (error.code === 1) {
            // PERMISSION_DENIED
            logger.warn('使用者拒絕了定位請求');
            toastMessage = '請開啟定位權限以使用定位功能';
        } else if (error.code === 2) {
            // POSITION_UNAVAILABLE (kCLErrorLocationUnknown)
            logger.warn('無法取得位置資訊 - GPS訊號不足或定位服務初始化中');
            toastMessage = '定位中，請稍候或移至空曠處以獲得更好的訊號';
        } else if (error.code === 3) {
            // TIMEOUT
            logger.warn('定位請求逾時');
            toastMessage = '定位請求逾時，請稍後再試';
        } else {
            logger.warn('未知的定位錯誤:', error);
            toastMessage = '定位功能暫時無法使用，請稍後再試';
        }
        
        // 顯示 Toast 提示
        toast?.show(toastMessage, 'warning', 10000);
    });
    
    // 監聽定位成功事件
    geolocateControl.on('geolocate', (position) => {
        logger.info('定位成功:', position.coords.latitude, position.coords.longitude);
    });
    
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
        
        // 自動觸發定位（在地圖載入後）
        // 檢查是否支援地理定位
        if ('geolocation' in navigator) {
            setTimeout(() => {
                try {
                    geolocateControl.trigger();
                } catch (error) {
                    logger.warn('自動定位失敗:', error);
                    toast?.show('定位功能無法使用，請確認已開啟定位權限', 'warning', 5000);
                }
            }, 1000);
        } else {
            logger.warn('此瀏覽器不支援地理定位功能');
            toast?.show('您的瀏覽器不支援地理定位功能', 'error', 5000);
        }
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