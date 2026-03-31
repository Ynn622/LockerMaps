<script setup lang="ts">
import { ref, provide, onMounted, onBeforeUnmount } from 'vue';
import Toast from './pages/components/Toast.vue';
import { startVersionChecker } from '@/utilities/versionChecker';

const toastRef = ref<InstanceType<typeof Toast> | null>(null);
let stopVersionCheck: (() => void) | null = null;
let reloadTimer: number | null = null;
const AUTO_RELOAD_DELAY_MS = 10000;
const AUTO_RELOAD_DELAY_SEC = AUTO_RELOAD_DELAY_MS / 1000;

// 提供 Toast 給所有子組件使用
provide('toast', toastRef);

onMounted(() => {
  stopVersionCheck = startVersionChecker({
    onVersionMismatch: ({ remoteVersion }) => {
      toastRef.value?.show(
        `偵測到新版本（${remoteVersion}），${AUTO_RELOAD_DELAY_SEC} 秒後將自動重新整理頁面。`,
        'info',
        AUTO_RELOAD_DELAY_MS
      );

      if (reloadTimer) {
        window.clearTimeout(reloadTimer);
      }

      reloadTimer = window.setTimeout(() => {
        window.location.reload();
      }, AUTO_RELOAD_DELAY_MS);
    },
  });
});

onBeforeUnmount(() => {
  stopVersionCheck?.();
  stopVersionCheck = null;

  if (reloadTimer) {
    window.clearTimeout(reloadTimer);
    reloadTimer = null;
  }
});
</script>

<template>
  <router-view />
  
  <!-- 全局 Toast 組件 -->
  <Toast ref="toastRef" />
</template>
