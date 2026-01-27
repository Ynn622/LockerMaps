<template>
    <section class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 md:p-8">
        <!-- 標題區塊 -->
        <div class="flex items-center gap-2 md:gap-3 mb-2 md:mb-3">
            <i :class="['text-xl md:text-2xl', iconClass]"></i>
            <h2 class="text-xl md:text-2xl font-bold text-gray-800 dark:text-gray-100">{{ title }}</h2>
        </div>
        
        <!-- 內容插槽 -->
        <div class="text-gray-700 dark:text-gray-300 text-sm md:text-base">
            <slot></slot>
        </div>
    </section>
</template>

<script setup lang="ts">
defineProps<{
    title: string;
    iconClass: string;
}>();
</script>
