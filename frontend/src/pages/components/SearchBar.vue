<template>
    <div ref="searchBarRef" class="absolute top-2.5 right-15 z-10 w-[80vw] md:w-[350px] z-30">
        <div class="relative items-center">
            <input
                v-model="searchQuery"
                @input="handleSearch"
                @focus="handleFocus"
                type="text"
                placeholder="搜尋站點名稱..."
                class="w-full px-3 py-2 md:py-2.5 pr-10 bg-white dark:bg-gray-800 dark:text-gray-100 border-2 border-gray-300/90 dark:border-gray-600 rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-semibold text-base placeholder:text-gray-400 dark:placeholder:text-gray-500"
            />
            <i class="fa-solid fa-magnifying-glass absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"></i>
            
            <!-- 清除按鈕 -->
            <button
                v-if="searchQuery"
                @click="clearSearch"
                class="absolute right-9 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
            >
                <i class="fa-solid fa-circle-xmark text-base"></i>
            </button>
        </div>
        
        <!-- 搜尋結果下拉列表 -->
        <div
            v-if="showResults && searchQuery && filteredStations.length > 0"
            class="absolute top-full mt-1 w-full bg-white dark:bg-gray-800 border-2 border-gray-300/90 dark:border-gray-600 rounded shadow-lg max-h-[35dvh] overflow-y-auto"
        >
            <div
                v-for="station in filteredStations"
                :key="station.station"
                @click="selectStation(station)"
                class="px-3 md:px-4 py-2.5 md:py-3 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition"
            >
                <div class="flex items-start gap-2">
                    <i class="fa-solid fa-location-dot mt-1 dark:text-gray-300"></i>
                    <div class="flex-1">
                        <div class="flex items-start justify-between gap-2">
                            <div class="font-semibold text-gray-800 dark:text-gray-100 text-sm">{{ station.station }}</div>
                            <span class="text-xs px-2 py-0.5 rounded bg-gradient-to-r text-white flex-shrink-0" :class="getTypeDisplayClass(station.type)">{{station.type }}</span>
                        </div>
                        <div class="flex gap-2 mt-1" v-if="station.tag && station.tag.length > 0">
                            <span v-for="tag in station.tag" :key="tag"
                                :class="['text-xs px-2 py-0.5 rounded text-white', getTagColorClass(tag)]">
                                {{ tag }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 無結果提示 -->
        <div
            v-if="showResults && searchQuery && filteredStations.length === 0"
            class="absolute top-full mt-1 w-full bg-white dark:bg-gray-800 border-2 border-gray-300/90 dark:border-gray-600 rounded shadow-lg px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center"
        >
            <i class="fa-solid fa-circle-exclamation mr-1"></i>
            找不到符合的站點
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { StationData } from '../../utilities/lockerApi';
import { getTagColorClass, getTypeDisplayClass } from '@/utilities/colorUtils';

const props = defineProps<{
    stations: StationData[];
}>();

const emit = defineEmits<{
    select: [station: StationData];
}>();

const searchQuery = ref('');
const showResults = ref(false);
const searchBarRef = ref<HTMLElement | null>(null);

// 過濾站點
const filteredStations = computed(() => {
    if (!searchQuery.value.trim()) return [];
    
    const query = searchQuery.value.toLowerCase().trim();
    return props.stations
        .filter(station => 
            station.station?.toLowerCase().includes(query) ||
            station.type?.toLowerCase().includes(query)
        )
        .slice(0, 10); // 最多顯示 10 筆結果
});

// 選擇站點
const selectStation = (station: StationData) => {
    emit('select', station);
    showResults.value = false;
};

// 清除搜尋
const clearSearch = () => {
    searchQuery.value = '';
    showResults.value = false;
};

// 點擊外部關閉結果
const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (searchBarRef.value && !searchBarRef.value.contains(target)) {
        showResults.value = false;
    }
};

// 處理搜尋輸入
const handleSearch = () => {
    showResults.value = true;
};

// 處理聚焦事件
const handleFocus = () => {
    if (searchQuery.value.trim()) {
        showResults.value = true;
    }
};

// 監聽點擊外部事件
if (typeof window !== 'undefined') {
    document.addEventListener('click', handleClickOutside);
}
</script>

<style scoped>
/* 自定義滾動條 */
div::-webkit-scrollbar {
    width: 6px;
}

div::-webkit-scrollbar-track {
    background: #f1f1f1;
}

div::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
}

div::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>
