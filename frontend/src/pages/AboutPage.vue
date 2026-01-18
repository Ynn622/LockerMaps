<template>
    <div class="flex flex-col w-full min-h-screen bg-gray-50">
        <Nav />
        
        <div class="flex-1 w-full max-w-4xl mx-auto px-4 pt-8 md:pt-12">
            <!-- 標題區塊 -->
            <div class="text-center mb-8">
                <h1 class="text-3xl md:text-5xl font-bold text-gray-800 mb-4">關於 LockerMaps</h1>
                <p class="text-sm md:text-lg text-gray-600">台灣最便利的置物櫃速查平台</p>
            </div>

            <!-- 網頁介紹 -->
            <div class="flex flex-col gap-4 md:gap-6">
                <SectionCard class="scroll-card" title="網頁介紹" icon-class="fa-solid fa-circle-info text-blue-500">
                    <div class="space-y-3">
                        <p class="indent-7">
                            <strong>LockerMaps</strong> 是一個專為台灣使用者設計的置物櫃查詢平台，
                            整合全台各地的置物櫃資訊，包括火車站、捷運站、商場等公共場所。
                        </p>
                        <div class="grid md:grid-cols-2 gap-4 mt-6">
                            <div class="flex items-start gap-3">
                                <i class="fa-solid fa-map-location-dot text-green-500 text-xl mt-1"></i>
                                <div>
                                    <h3 class="font-semibold text-gray-800 mb-1">即時地圖定位</h3>
                                    <p class="text-sm text-gray-600">快速找到離你最近的置物櫃位置</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <i class="fa-solid fa-database text-purple-500 text-xl mt-1"></i>
                                <div>
                                    <h3 class="font-semibold text-gray-800 mb-1">完整資訊查詢</h3>
                                    <p class="text-sm text-gray-600">提供詳細的置物櫃規格與收費資訊</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <i class="fa-solid fa-mobile-screen-button text-orange-500 text-xl mt-1"></i>
                                <div>
                                    <h3 class="font-semibold text-gray-800 mb-1">響應式設計</h3>
                                    <p class="text-sm text-gray-600">支援手機、平板、電腦多種裝置</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <i class="fa-solid fa-bolt text-yellow-500 text-xl mt-1"></i>
                                <div>
                                    <h3 class="font-semibold text-gray-800 mb-1">快速載入</h3>
                                    <p class="text-sm text-gray-600">優化效能，提供流暢使用體驗</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </SectionCard>

                <!-- 資料來源 -->
                <SectionCard class="scroll-card" title="資料來源" icon-class="fa-solid fa-book text-green-500">
                    <div class="space-y-4">
                        <p class="indent-7">
                            本平台的置物櫃資料來自以下開放資料來源，確保資訊的準確性與即時性：
                        </p>
                        <div class="space-y-3">
                            <div class="flex flex-col gap-1 border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 rounded-r">
                                <a href="https://www.metro.taipei/cp.aspx?n=074C9E96AEC24806"
                                    class="font-semibold text-gray-800">台北捷運 - 置物櫃服務</a>
                                <p class="text-sm text-gray-600">台北捷運公開寄物櫃資料</p>
                            </div>
                            <div
                                class="flex flex-col gap-1 border-l-4 border-orange-500 pl-4 py-2 bg-orange-50 rounded-r">
                                <a href="https://owlocker.com/#/querysite"
                                 class="font-semibold text-gray-800">OWL Locker 智慧型寄物櫃</a>
                                <p class="text-sm text-gray-600">全台最大的智慧型寄物櫃平台</p>
                            </div>
                            <div class="flex flex-col gap-1 border-l-4 border-gray-500 pl-4 py-2 bg-gray-50 rounded-r">
                                <a href="https://lockerinfo.autosale.com.tw/"
                                   class="font-semibold text-gray-800">臺鐵置物櫃資訊</a>
                                <p class="text-sm text-gray-600">臺鐵台北10站置物櫃資料</p>
                            </div>
                            <div class="flex flex-col gap-1 border-l-4 border-purple-500 pl-4 py-2 bg-purple-50 rounded-r">
                                <a class="font-semibold text-gray-800">使用者回報</a>
                                <p class="text-sm text-gray-600">熱心使用者提供的最新置物櫃位置資訊</p>
                            </div>
                        </div>
                        <p class="text-sm text-gray-500 mt-4">
                            <i class="fa-solid fa-circle-exclamation mr-1"></i>
                            註：資料會定期更新，如有異動或錯誤，歡迎透過意見回饋告訴我們～
                        </p>
                    </div>
                </SectionCard>

                <!-- 意見回饋 -->
                <SectionCard class="scroll-card" title="意見回饋" icon-class="fa-solid fa-comments text-orange-500">
                    <div class="mb-6">
                        <p class="indent-7">
                            您的意見對我們非常重要！如果您在使用過程中有任何建議、發現錯誤資訊，
                            或想要分享新的置物櫃位置，歡迎透過以下表單告訴我們。
                        </p>
                    </div>
                    
                    <!-- 回饋表單 -->
                    <form @submit.prevent="submitFeedback" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                <i class="fa-solid fa-tag mr-1"></i>回饋類型
                            </label>
                            <select 
                                v-model="feedbackForm.type" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            >
                                <option value="">請選擇回饋類型</option>
                                <option value="suggestion">建議</option>
                                <option value="bug">錯誤回報</option>
                                <option value="data">資料更新/新增</option>
                                <option value="other">其他</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                <i class="fa-solid fa-user mr-1"></i>暱稱
                            </label>
                            <input 
                                v-model="feedbackForm.name" 
                                type="text" 
                                placeholder="請輸入您的暱稱"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            />
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                <i class="fa-solid fa-envelope mr-1"></i>Email（選填）
                            </label>
                            <input 
                                v-model="feedbackForm.email" 
                                type="email" 
                                placeholder="請輸入您的 Email"
                                @input="handleEmailInput"
                                class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                :class="emailError ? 'border-red-500' : 'border-gray-300'"
                            />
                            <p v-if="emailError" class="text-red-500 text-sm mt-1">
                                <i class="fa-solid fa-circle-exclamation mr-1"></i>{{ emailError }}
                            </p>
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                <i class="fa-solid fa-message mr-1"></i>意見內容
                            </label>
                            <textarea 
                                v-model="feedbackForm.content" 
                                rows="6" 
                                minlength="5"
                                placeholder="請詳細描述您的意見或建議..."
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                required
                            ></textarea>
                        </div>

                        <div class="flex gap-4">
                            <button 
                                type="submit" 
                                :disabled="isSubmitting"
                                class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                required
                            >
                                <i class="fa-solid fa-paper-plane mr-2"></i>
                                {{ isSubmitting ? '送出中...' : '送出回饋' }}
                            </button>
                            <button 
                                type="button" 
                                @click="resetForm"
                                class="px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition duration-200"
                            >
                                <i class="fa-solid fa-rotate-right mr-2"></i>清除
                            </button>
                        </div>
                    </form>
                </SectionCard>
            </div>

            <!-- Footer -->
            <footer class="text-center text-gray-500 text-sm py-8">
                <p>© 2026 LockerMaps. Made with <i class="fa-solid fa-heart text-red-500"></i> in Taiwan</p>
            </footer>
        </div>

        <!-- Toast 提示 -->
        <Toast ref="toastRef" />
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Nav from './components/Nav.vue';
import Toast from './components/Toast.vue';
import SectionCard from './components/SectionCard.vue';
import { logger } from '../utilities/logger';
import { API_BASE_URL } from '../utilities/apiConfig';

// 註冊 GSAP 插件
gsap.registerPlugin(ScrollTrigger);

const toastRef = ref<InstanceType<typeof Toast> | null>(null);
const isSubmitting = ref(false);
const emailError = ref('');

// 回饋表單資料
const feedbackForm = reactive({
    type: '',
    name: '',
    email: '',
    content: ''
});

// Email 格式驗證
const validateEmail = (email: string): boolean => {
    if (!email) return true; // 如果沒有輸入，不驗證
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// 監聽 email 變化並驗證
const handleEmailInput = () => {
    if (feedbackForm.email && !validateEmail(feedbackForm.email)) {
        emailError.value = 'Email 格式不正確';
    } else {
        emailError.value = '';
    }
};

// 送出回饋
const submitFeedback = async () => {
    try {
        // 驗證 email 格式
        if (feedbackForm.email && !validateEmail(feedbackForm.email)) {
            toastRef.value?.show('請輸入正確的 Email 格式', 'error', 3000);
            return;
        }
        
        isSubmitting.value = true;
        logger.func.start('submitFeedback', [feedbackForm]);
        
        // 呼叫後端 API
        const response = await fetch(`${API_BASE_URL}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackForm)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '送出失敗');
        }
        
        const result = await response.json();
        
        logger.func.success('submitFeedback', [result]);
        
        toastRef.value?.show('感謝您的回饋！我們會盡快處理。', 'success', 5000);
        
        // 清空表單
        resetForm();
    } catch (error) {
        logger.func.error('submitFeedback', []);
        logger.error('送出回饋失敗:', error);
        toastRef.value?.show('送出失敗，請稍後再試', 'error', 5000);
    } finally {
        isSubmitting.value = false;
    }
};

// 重置表單
const resetForm = () => {
    feedbackForm.type = '';
    feedbackForm.name = '';
    feedbackForm.email = '';
    feedbackForm.content = '';
    emailError.value = '';
};

// GSAP ScrollTrigger 動畫
onMounted(() => {
    // 為每個卡片設定滑入動畫
    const cards = document.querySelectorAll('.scroll-card');
    
    cards.forEach((card) => {
        gsap.fromTo(card,
            {
                opacity: 0,
                x: -100,
            },
            {
                opacity: 1,
                x: 0,
                y: 0,
                duration: 0.8,
                ease: 'power3.out',
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    end: 'top 60%',
                    toggleActions: 'play none none none',
                    // markers: true // 開發時可以打開看觸發點
                }
            }
        );
    });

    // 標題淡入效果
    gsap.from('.text-center', {
        opacity: 0,
        y: -50,
        duration: 1,
        ease: 'power2.out'
    });
});
</script>

<style scoped>
/* 平滑滾動 */
html {
    scroll-behavior: smooth;
}

/* 卡片初始狀態 - 確保在 GSAP 動畫載入前不顯示 */
.scroll-card {
    opacity: 0;
}
</style>
