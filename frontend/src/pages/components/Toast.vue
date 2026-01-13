<template>
    <Transition name="toast">
        <div v-if="visible" 
             :class="['fixed z-50 top-20 left-1/2 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 break-words max-w-[80dvw] toast-container', typeClass]">
            <i :class="iconClass"></i>
            <span class="text-sm font-medium">{{ message }}</span>
        </div>
    </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

type ToastType = 'success' | 'error' | 'warning' | 'info';

const visible = ref(false);
const message = ref('');
const type = ref<ToastType>('info');
let timer: number | null = null;

const typeClass = computed(() => {
    const classes = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white'
    };
    return classes[type.value];
});

const iconClass = computed(() => {
    const icons = {
        success: 'fa-solid fa-circle-check text-lg',
        error: 'fa-solid fa-circle-exclamation text-lg',
        warning: 'fa-solid fa-triangle-exclamation text-lg',
        info: 'fa-solid fa-circle-info text-lg'
    };
    return icons[type.value];
});

const show = (msg: string, toastType: ToastType = 'info', duration: number = 3000) => {
    // 清除之前的計時器
    if (timer) {
        clearTimeout(timer);
    }
    
    message.value = msg;
    type.value = toastType;
    visible.value = true;
    
    // 自動隱藏
    timer = setTimeout(() => {
        hide();
    }, duration);
};

const hide = () => {
    visible.value = false;
    if (timer) {
        clearTimeout(timer);
        timer = null;
    }
};

defineExpose({
    show,
    hide
});
</script>

<style scoped>
.toast-container {
    transform: translateX(-50%);
}

.toast-enter-active,
.toast-leave-active {
    transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
    opacity: 0;
    transform: translateX(-50%) translateY(-30px);
}
</style>
