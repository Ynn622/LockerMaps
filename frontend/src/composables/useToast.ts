import { inject, type Ref } from 'vue';
import type Toast from '@/pages/components/Toast.vue';

/**
 * 使用全局 Toast 組件的 Hook
 * @returns Toast 組件實例
 */
export const useToast = () => {
    const toast = inject<Ref<InstanceType<typeof Toast> | null>>('toast');
    
    if (!toast) {
        console.warn('Toast component is not provided. Make sure Toast is mounted in App.vue');
        return null;
    }
    
    return toast.value;
};
