<template>
    <div v-if="isLoading" 
         ref="overlayRef" 
         class="fixed inset-0 bg-white/70 dark:bg-gray-900/80 backdrop-blur-xl flex items-center justify-center z-[9999]">
        <div ref="containerRef" 
             class="flex flex-col items-center gap-6">
            <!-- 旋轉圖標 -->
            <div ref="iconRef" class="relative">
                <i class="fa-solid fa-box-archive text-5xl text-blue-600 dark:text-blue-400"></i>
            </div>
            
            <!-- 載入文字 -->
            <div class="flex flex-col items-center gap-2">
                <p class="text-lg font-semibold text-gray-700 dark:text-gray-200">{{ text }}</p>
                <div class="flex gap-2">
                    <span ref="dot1" class="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 opacity-50"></span>
                    <span ref="dot2" class="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 opacity-50"></span>
                    <span ref="dot3" class="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 opacity-50"></span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import gsap from 'gsap';

const isLoading = ref(true);
const text = ref('載入置物櫃資料中');

const overlayRef = ref<HTMLElement | null>(null);
const containerRef = ref<HTMLElement | null>(null);
const iconRef = ref<HTMLElement | null>(null);
const dot1 = ref<HTMLElement | null>(null);
const dot2 = ref<HTMLElement | null>(null);
const dot3 = ref<HTMLElement | null>(null);

const show = async (loadingText: string = '載入中') => {
    text.value = loadingText;
    isLoading.value = true;
    
    await nextTick();
    
    // 淡入效果
    if (overlayRef.value) {
        gsap.fromTo(overlayRef.value,
            { opacity: 0 },
            { opacity: 1, duration: 0.3, ease: 'power2.out' }
        );
    }
    
    // 容器放大淡入
    if (containerRef.value) {
        gsap.fromTo(containerRef.value,
            { scale: 0.8, opacity: 0 },
            { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(1.7)', delay: 0.1 }
        );
    }
    
    // 圖標彈跳動畫（循環）
    if (iconRef.value) {
        gsap.to(iconRef.value, {
            y: -20,
            duration: 0.6,
            ease: 'power1.inOut',
            repeat: -1,
            yoyo: true
        });
    }
    
    // 點點動畫（循環）
    if (dot1.value && dot2.value && dot3.value) {
        gsap.to(dot1.value, {
            scale: 1.5,
            opacity: 1,
            duration: 0.6,
            ease: 'power1.inOut',
            repeat: -1,
            yoyo: true,
            delay: 0
        });
        gsap.to(dot2.value, {
            scale: 1.5,
            opacity: 1,
            duration: 0.6,
            ease: 'power1.inOut',
            repeat: -1,
            yoyo: true,
            delay: 0.2
        });
        gsap.to(dot3.value, {
            scale: 1.5,
            opacity: 1,
            duration: 0.6,
            ease: 'power1.inOut',
            repeat: -1,
            yoyo: true,
            delay: 0.4
        });
    }
};

const hide = () => {
    if (overlayRef.value) {
        gsap.to(overlayRef.value, {
            opacity: 0,
            duration: 0.3,
            ease: 'power2.in',
            onComplete: () => {
                isLoading.value = false;
                // 停止所有動畫
                gsap.killTweensOf([iconRef.value, dot1.value, dot2.value, dot3.value]);
            }
        });
    }
};

defineExpose({
    show,
    hide
});
</script>
