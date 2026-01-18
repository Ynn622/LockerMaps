<script setup lang="ts">
import { ref, provide } from 'vue';
import Toast from './pages/components/Toast.vue';

const toastRef = ref<InstanceType<typeof Toast> | null>(null);

// 提供 Toast 給所有子組件使用
provide('toast', toastRef);
</script>

<template>
  <router-view />
  
  <!-- 全局 Toast 組件 -->
  <Toast ref="toastRef" />
</template>
