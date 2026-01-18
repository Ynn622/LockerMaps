<template>
    <!-- 頂部標題列 Nav -->
    <div class="bg-gray-100 shadow-md flex items-center justify-between px-2.5 md:px-4 py-2.5">
        <a href="/" class="flex items-center gap-2">
            <img src="../../assets/logo.png" class="h-10 aspect-square" alt="LockerMaps Logo">
            <span class="flex flex-col">
                <span class="text-xl text-gray-800 font-bold">LockerMaps</span>
                <p class="text-xs text-gray-600">台灣置物櫃速查</p>
            </span>
        </a>
        <!-- 電腦版：選單列 -->
        <div class="hidden md:flex items-center px-3 gap-8 rounded-md text-sm font-bold">
            <button @click="shared()" class="text-gray-700 hover:text-gray-900">推薦朋友</button>
            <router-link to="/about" class="text-gray-700 hover:text-gray-900">關於我們</router-link>
        </div>
        <!-- 手機版：漢堡選單 -->
        <div class="flex md:hidden" @click="toggleMenu()">
            <i class="fa-solid fa-bars text-gray-700 hover:text-gray-900 text-2xl"></i>
        </div>
    </div>
    <!-- 手機版選單下拉 -->
    <div id="mobileMenu" class="flex flex-col md:hidden absolute top-16 z-40 px-4 py-3 gap-5 bg-white shadow-md w-full text-sm font-bold opacity-0 overflow-hidden items-start">
        <button @click="shared()" class="text-gray-700 hover:text-gray-900">推薦朋友</button>
        <router-link to="/about" class="text-gray-700 hover:text-gray-900">關於我們</router-link>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import gsap from 'gsap';
import { useToast } from '@/composables/useToast';

const toast = useToast();

const shared = () => {
    const shareData = {
        title: 'LockerMaps - 台灣置物櫃速查',
        text: '快速查找台灣各地的置物櫃位置與資訊！',
        url: window.location.origin
    };

    if (navigator.share) {
        navigator.share(shareData)
            .then(() => {
                toast?.show('感謝您的分享！', 'success');
            })
            .catch((error) => {
                toast?.show('分享失敗，請稍後再試。', 'error');
                console.error('分享失敗:', error);
            });
    } else {
        // 複製連結到剪貼簿
        try {
            navigator.clipboard.writeText(shareData.url);
            toast?.show('已複製連結到剪貼簿', 'success');
        } catch (error) {
            toast?.show('複製連結失敗', 'error');
        }
    }
};

const isMenuOpen = ref(false);

const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
    if (isMenuOpen.value) {
        showMobileMenu();
    } else {
        hideMobileMenu();
    }
};

const showMobileMenu = () => {
    const menu = document.getElementById('mobileMenu');
    gsap.to(menu,
        { height: 'auto', opacity: 1, duration: 0.3, ease: 'power2.out' }
    );
};

const hideMobileMenu = () => {
    const menu = document.getElementById('mobileMenu');
    gsap.to(menu, {
        height: -10,
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in'
    });
};

</script>