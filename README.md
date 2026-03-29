# LockerMaps 台灣置物櫃地圖

<p align="center">
  <img src="https://img.shields.io/badge/Vue.js-4FC08D?logo=vue.js&logoColor=white" alt="Vue.js">
  <img src="https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/TailwindCSS-06B6D4?logo=tailwindcss&logoColor=white" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Firebase-FFCA28?logo=firebase&logoColor=black" alt="Firebase">
</p>

<p align="center">
  <strong>台灣置物櫃速查！</strong><br>
  <em>捷運、台鐵、高鐵、百貨商場置物櫃資訊一把抓！</em>
</p>

---

## 🌟 專案介紹

LockerMaps 是一個幫助使用者快速尋找台灣各地置物櫃的互動式地圖應用。涵蓋交通樞紐與各大商圈，提供方便、即時的寄物櫃資訊查詢服務。包含直覺的地圖介面與標籤篩選功能。

## 🚀 核心功能

- 🗺️ **互動地圖查詢**: 整合 Mapbox GL，直覺拖曳尋找附近的置物櫃。
- 🔍 **分類篩選**: 支援捷運站、台鐵/高鐵站與百貨商場等分類篩選。
- 📝 **使用者反饋 (Feedback)**: 問題回報與建議系統。
- 📱 **RWD 響應式設計**: 手機、平板、電腦皆能順暢操作。
- 🌓 **深色/淺色模式**: 系統預設自適應主題切換。

## 🛠️ 技術棧 (Tech Stack)

### 前端 (Frontend)
- **核心**: Vue 3 (Composition API), Vite, TypeScript
- **樣式**: Tailwind CSS v4, CSS Variables
- **地圖**: Mapbox GL
- **動畫**: GSAP
- **工具庫**: VueUse, Vue Router

### 後端 (Backend)
- **框架**: Python FastAPI
- **資料庫**: Firebase (Firestore/Realtime DB)
- **部署**: Docker, Hugging Face Spaces (具備 CORS 與 Basic Auth 防護)

---

## 📂 專案結構

```text
Lockers/
├── backend/                # FastAPI 後端目錄
│   ├── API/                # 路由定義 (locker, feedback)
│   ├── services/           # 商業邏輯與資料庫操作
│   ├── util/               # 工具函式庫 (Config, Env, Logger)
│   ├── app.py              # FastAPI 進入點
│   └── Dockerfile          # 後端容器化設定
└── frontend/               # Vue 前端目錄
    ├── src/
    │   ├── assets/         # 靜態資源
    │   ├── components/     # 共用 UI 元件 (地圖, 搜尋, 彈出視窗)
    │   ├── composables/    # 組合式函數 (DarkMode, Toast)
    │   ├── pages/          # 頁面檢視 (Home, About)
    │   ├── router/         # Vue Router 定義
    │   └── utilities/      # API 請求與工具函式
    └── tailwind.config.ts  # Tailwind CSS 設定
```

## 📄 授權

本專案僅供學習與娛樂用途。

---

<p align="center">
  <sub>© 2026 LockerMaps. All rights reserved.</sub>
</p>
