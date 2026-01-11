<template>
    <div v-if="isVisible && stationData" 
         ref="panelRef"
         :class="[
             'detail-panel',
             'bg-white shadow-2xl overflow-hidden flex flex-col',
             isMobile ? 'mobile' : 'desktop'
         ]">
            
            <!-- 標題列 -->
            <div :class="['bg-gradient-to-br', getTypeDisplayClass(stationData.type), 'text-white px-4 py-3 flex justify-between items-center']">
                <div class="flex flex-col">
                    <div class="flex gap-1 items-center text-lg md:text-xl">
                        <i class="fa-solid fa-location-dot"></i>
                        <span class="font-bold">{{ stationData.station }}</span>
                    </div>
                    <div class="flex gap-2 mt-1">
                        <span class="text-xs bg-black/30 px-2 py-0.5 rounded">{{ getTypeDisplayName(stationData.type) }}</span>
                        <span v-for="tag in stationData.tag" 
                              :key="tag"
                              :class="['text-xs px-2 py-0.5 rounded', getTagColorClass(tag)]">
                            {{ tag }}
                        </span>
                    </div>
                </div>
                <button @click="close" 
                        class="text-white bg-transparent rounded-full w-8 h-8 flex items-center justify-center transition">
                    <i class="fa-solid fa-times text-xl"></i>
                </button>
            </div>

            <!-- 內容區域 -->
            <div class="flex-1 overflow-y-auto p-3 md:p-4">
                <!-- 總覽資訊 -->
                <div class="mb-2 px-3.5 py-2.5 bg-blue-50 rounded-lg">
                    <div class="flex justify-between items-center">
                        <span class="text-sm md:text-base text-gray-600">空櫃 / 總櫃數</span>
                        <div>
                            <span class="text-xl md:text-2xl font-bold text-blue-600">{{ totalEmpty }}</span> / 
                            <span class="text-base md:text-lg font-semibold text-gray-700">{{ totalCount }}</span>
                        </div>
                    </div>
                </div>

                <!-- 置物櫃列表 -->
                <div class="space-y-1.5">
                    <div v-for="(detail, index) in stationData.details" 
                         :key="index"
                         class="bg-white border border-gray-200 rounded-lg px-3 py-2 hover:shadow-md transition">
                        <!-- 上半部 -->
                        <div class="flex justify-between items-start">
                            <!-- 左上：位置 -->
                            <div class="flex-1 font-semibold text-gray-800">
                                {{ detail.loc }}
                            </div>
                            <!-- 右上：空櫃/總櫃 -->
                            <div class="text-right">
                                <span :class="getEmptyClass(detail.empty, detail.total)" class="text-lg font-bold">{{ detail.empty }}</span>
                                <span class="text-gray-400 mx-1">/</span>
                                <span class="text-gray-600 font-semibold">{{ detail.total ?? '-' }}</span>
                            </div>
                        </div>
                        
                        <!-- 下半部 -->
                        <div class="flex justify-between items-center">
                            <!-- 左下：尺寸 價格 -->
                            <div class="flex items-center gap-2">
                                <span class="px-2 py-0.5 rounded font-semibold text-sm" :class="getSizeBadgeClass(detail.size)">
                                    {{ detail.size }}
                                </span>
                                <span class="text-sm text-gray-600">{{ detail.price }}</span>
                            </div>
                            <!-- 右下：櫃號 -->
                            <div v-if="detail.id != 0">
                                <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-semibold">
                                    第 {{ detail.id }} 櫃
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import type { StationData } from '@/utilities/lockerApi';
import { useBreakpoints, breakpointsTailwind } from '@vueuse/core';
import gsap from 'gsap';
import { getTypeDisplayClass, getTypeDisplayName, getTagColorClass } from '@/utilities/colorUtils';

const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller('md'); // < md

const isVisible = ref(false);
const stationData = ref<StationData | null>(null);
const panelRef = ref<HTMLElement | null>(null);

// 總空櫃數
const totalEmpty = computed(() => {
    if (!stationData.value) return 0;
    return stationData.value.details.reduce((sum, d) => sum + d.empty, 0);
});

// 總櫃數
const totalCount = computed(() => {
    if (!stationData.value) return 0;
    const total = stationData.value.details.reduce((sum, d) => {
        return sum + (d.total ?? 0);
    }, 0);
    return total===0 ? '-' : total;
});

// 顯示詳細資訊
const show = async (data: StationData) => {
    stationData.value = data;
    isVisible.value = true;
    
    await nextTick();
    
    if (panelRef.value) {
        if (isMobile.value) {
            // 手機版：從下方滑入
            gsap.fromTo(panelRef.value,
                { y: '100%' },
                { y: 0, duration: 0.4, ease: 'power2.out' }
            );
        } else {
            // 電腦版：從左方滑入
            gsap.fromTo(panelRef.value,
                { x: '-100%' },
                { x: 0, duration: 0.4, ease: 'power2.out' }
            );
        }
    }
};

// 關閉面板
const close = () => {
    if (panelRef.value) {
        if (isMobile.value) {
            // 手機版：向下滑出
            gsap.to(panelRef.value, {
                y: '100%',
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => {
                    isVisible.value = false;
                    stationData.value = null;
                }
            });
        } else {
            // 電腦版：向左滑出
            gsap.to(panelRef.value, {
                x: '-100%',
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => {
                    isVisible.value = false;
                    stationData.value = null;
                }
            });
        }
    }
};

// 判斷數量狀態
const getNumStatus = (empty: number, total: number) => {
    let rate = total > 0 ? empty / total : 0;
    if (total === 0) return 'no-data';
    if (rate === 0) return 'full';
    if (rate <= 0.2) return 'almost-full';
    return 'available';
};

// 尺寸徽章樣式
const getSizeBadgeClass = (size: string) => {
    if (size === 'L') return 'bg-purple-100 text-purple-700';
    if (size === 'S') return 'bg-blue-100 text-blue-700';
    if (size === '手機充電') return 'bg-amber-100 text-amber-700 text-xs';
    return 'bg-gray-100 text-gray-700';
};

// 空櫃數顏色
const getEmptyClass = (empty: number, total: number | null) => {
    if (empty === 0) return 'text-red-600 font-bold';
    const status = getNumStatus(empty, total ?? 0);
    if (status === 'no-data') return 'text-green-600 font-semibold';
    if (status === 'full') return 'text-red-600 font-bold';
    if (status === 'almost-full') return 'text-orange-600 font-semibold';
    return 'text-green-600 font-semibold';
};

defineExpose({
    show,
    close
});
</script>

<style scoped>
.detail-panel {
    position: fixed;
    z-index: 1000;
}

.detail-panel.desktop {
    left: 0;
    top: 60px;
    bottom: 0;
    width: 420px;
    border-radius: 0 0.5rem 0.5rem 0;
    max-width: 90vw;
    border-right: 1px solid #e5e7eb;
}

.detail-panel.mobile {
    left: 0;
    right: 0;
    bottom: 0;
    max-height: 60vh;
    border-radius: 1rem 1rem 0 0;
    width: 100dvw;
    border-right: 1px solid #e5e7eb;
}
</style>
