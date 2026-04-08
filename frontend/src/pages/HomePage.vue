<template>
    <div class="flex flex-col w-full h-[100dvh]">
        <Nav flow="absolute" />

        <!-- Mapbox 地圖容器 -->
        <div ref="mapContainer" class="flex-1 w-full h-full relative">
            <!-- 搜尋列 -->
            <SearchBar :stations="lockerStations" @select="handleStationSelect" />

            <!-- 重新載入按鈕 -->
            <button @click="reloadLockerData" :disabled="isReloading"
                class="absolute md:bottom-[24px] bottom-[10px] right-[8px] z-10 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 p-1.5 rounded shadow-md transition duration-200 border-gray-300/90 dark:border-gray-600 border-2 rounded-sm disabled:opacity-10 disabled:cursor-not-allowed"
                title="重新載入置物櫃資料中">
                <i :class="['fa-solid fa-rotate-right text-sm', { 'animate-spin': isReloading }]"></i>
            </button>

            <!-- 資料更新時間 -->
            <div v-if="lastUpdateTime" 
                @click="showTooltip = !showTooltip"
                class="absolute md:bottom-[24px] bottom-[10px] right-[48px] z-10 bg-white/90 dark:bg-gray-800/90 text-gray-600 dark:text-gray-400 px-2 py-1 rounded shadow-sm text-xs backdrop-blur-sm cursor-pointer active:scale-95 transition-transform">
                資料更新時間：{{ lastUpdateTime }}
                <!-- Tooltip -->
                <div v-show="showTooltip" class="absolute bottom-full right-0 mb-2 w-max max-w-[200px] bg-gray-800 dark:bg-gray-700 text-white text-xs px-3 py-2 rounded shadow-lg pointer-events-none">
                    資料每30秒更新一次，請手動點擊右方 <i class="fa-solid fa-rotate-right"></i> 更新資料！
                    <div class="absolute top-full right-4 -mt-1 border-4 border-transparent border-t-gray-800 dark:border-t-gray-700"></div>
                </div>
            </div>
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
const lastUpdateTime = ref<string>('');
const showTooltip = ref(false);

// 每個 marker 的尺寸更新函式集合
type MarkerUpdateFn = (size: number) => void;
const markerUpdateFns: MarkerUpdateFn[] = [];

const GEOJSON_OVERLAYS = [
    {
        key: 'bl',
        url: '/mapData/metro_bl_line_car_route.geojson',
        lineColor: '#0070bd',
        lineWidth: 3,
    },
    {
        key: 'br',
        url: '/mapData/metro_br_line_car_route.geojson',
        lineColor: '#c48c31',
        lineWidth: 3,
    },
    {
        key: 'g',
        url: '/mapData/metro_g_line_car_route.geojson',
        lineColor: '#008659',
        lineWidth: 3,
    },
    {
        key: 'g2',
        url: '/mapData/metro_g_line_car_route_2.geojson',
        lineColor: '#33a97a',
        lineWidth: 2,
    },
    {
        key: 'o',
        url: '/mapData/metro_o_line_car_route.geojson',
        lineColor: '#f8b61c',
        lineWidth: 3,
    },
    {
        key: 'o2',
        url: '/mapData/metro_o_line_car_route_2.geojson',
        lineColor: '#f8b61c',
        lineWidth: 3,
    },
    {
        key: 'r',
        url: '/mapData/metro_r_line_car_route.geojson',
        lineColor: '#cb2c30',
        lineWidth: 3,
    },
    {
        key: 'r2',
        url: '/mapData/metro_r_line_car_route_2.geojson',
        lineColor: '#dc6e71',
        lineWidth: 2,
    }
] as const;

/**
 * 根據 zoom level 線性插值出 marker 大小（px）
 * zoom 5 以下 → 12px，zoom 16 以上 → 30px
 */
const getMarkerSize = (zoom: number): number => {
    const minZoom = 5, maxZoom = 16;
    const minSize = 12, maxSize = 30;
    const t = Math.min(1, Math.max(0, (zoom - minZoom) / (maxZoom - minZoom)));
    return Math.round(minSize + t * (maxSize - minSize));
};

// 更新所有 marker 尺寸（用 rAF 節流，避免 zoom 事件打太頻繁）
let rafPending = false;
const updateMarkerSizes = () => {
    if (!map || rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => {
        rafPending = false;
        if (!map) return;
        const size = getMarkerSize(map.getZoom());
        markerUpdateFns.forEach(fn => fn(size));
    });
};

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
        
        // 更新資料載入時間
        const now = new Date();
        lastUpdateTime.value = `${now.getMonth() + 1}/${now.getDate()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        
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

/**
 * 依站點類型返回對應的 FontAwesome icon class
 */
const getMarkerIcon = (type: string): string => {
    switch (type) {
        case 'MRT': return 'fa-solid fa-train-subway';
        case 'TRA': return 'fa-solid fa-train';
        case 'OWL': return 'fa-solid fa-box-archive';
        default: return 'fa-solid fa-location-dot';
    }
};

// 添加標記點到地圖
const addMarkersToMap = () => {
    if (!map) return;

    // 清除舊標記
    markers.value.forEach((marker: mapboxgl.Marker) => marker.remove());
    markers.value = [];

    // 清空舊的尺寸更新函式
    markerUpdateFns.length = 0;

    // 添加新標記
    lockerStations.value.forEach(station => {
        if (!station.lat || !station.lng) return;

        const color = getMarkerColor(station.type);
        const icon = getMarkerIcon(station.type);

        // 外層容器 - 只給 Mapbox 用於定位，不加 transition（否則地圖拖動時 transform 會慢半拍飄移）
        const el = document.createElement('div');
        el.style.cssText = `
            width: 30px;
            height: 30px;
            cursor: pointer;
        `;

        // 內層視覺元素 - 負責外觀與 hover 動畫（scale 在此發生，不影響 Mapbox 定位）
        const inner = document.createElement('div');
        inner.style.cssText = `
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 3px solid ${color};
            background: rgba(255,255,255,0.95);
            box-shadow: 0 2px 8px rgba(0,0,0,0.25), 0 0 0 1.5px rgba(255,255,255,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            pointer-events: none;
        `;

        // 內部 icon
        const iconEl = document.createElement('i');
        iconEl.className = icon;
        iconEl.style.cssText = `
            color: ${color};
            font-size: 14px;
            pointer-events: none;
        `;
        inner.appendChild(iconEl);
        el.appendChild(inner);

        // Hover 動畫（套在 inner 上，不影響外層的定位 transform）
        el.addEventListener('mouseenter', () => {
            inner.style.transform = 'scale(1.25)';
            inner.style.boxShadow = `0 4px 16px rgba(0,0,0,0.3), 0 0 0 2px ${color}55`;
        });
        el.addEventListener('mouseleave', () => {
            inner.style.transform = 'scale(1)';
            inner.style.boxShadow = '0 2px 8px rgba(0,0,0,0.25), 0 0 0 1.5px rgba(255,255,255,0.6)';
        });

        // 建立 Mapbox Marker（使用自訂元素，anchor 設為 center）
        const marker = new mapboxgl.Marker({ element: el, anchor: 'center' })
            .setLngLat([station.lng, station.lat])
            .addTo(map!);

        // 點擊事件 - 顯示詳細資訊
        el.addEventListener('click', () => {
            logger.info('點擊站點:', station.station);
            detailPanel.value?.show(station);
        });

        // 註冊尺寸更新函式（zoom 變化時呼叫）
        markerUpdateFns.push((size: number) => {
            el.style.width = `${size}px`;
            el.style.height = `${size}px`;
            iconEl.style.fontSize = `${Math.round(size * 0.45)}px`;
        });

        markers.value.push(marker);
    });

    // 套用目前 zoom 的初始大小
    updateMarkerSizes();

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
        
        // 更新資料載入時間
        const now = new Date();
        lastUpdateTime.value = `${now.getMonth() + 1}/${now.getDate()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

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
        center: [station.lng, station.lat - (isMobile.value ? 0.005 : 0)],
        zoom: 14,
        duration: 1500,
        essential: true
    });

    // 延遲一下再顯示詳細資訊，讓地圖飛行動畫更流暢
    setTimeout(() => {
        detailPanel.value?.show(station);
    }, 800);
};

const addGeoJsonOverlays = async () => {
    if (!map) return;

    for (const overlay of GEOJSON_OVERLAYS) {
        const sourceId = `geojson-source-${overlay.key}`;
        const lineLayerId = `geojson-line-${overlay.key}`;

        try {
            const response = await fetch(overlay.url);
            if (!response.ok) {
                logger.warn(`GeoJSON 載入失敗 (${overlay.url}):`, response.status);
                continue;
            }

            const data = await response.json();

            if (!map.getSource(sourceId)) {
                map.addSource(sourceId, {
                    type: 'geojson',
                    data,
                });
            }

            if (!map.getLayer(lineLayerId)) {
                map.addLayer({
                    id: lineLayerId,
                    type: 'line',
                    source: sourceId,
                    paint: {
                        'line-color': overlay.lineColor,
                        'line-width': overlay.lineWidth,
                        'line-opacity': 0.9,
                    },
                });
            }

            logger.info(`GeoJSON 疊圖完成: ${overlay.url}`);
        } catch (error) {
            logger.error(`GeoJSON 疊圖失敗 (${overlay.url}):`, error);
        }
    }
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

    // 監聽 zoom 事件，動態縮放 marker 大小
    map.on('zoom', updateMarkerSizes);

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

        // 載入 public/mapData 下的 GeoJSON 疊圖
        addGeoJsonOverlays();

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
    markerUpdateFns.length = 0;

    map?.remove();
    map = null;
});

// 導出 map 實例供外部使用
defineExpose({
    map
});
</script>
