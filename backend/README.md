# LockerMaps API

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
</p>

---


## 💻 本地端開發指南

### 環境需求
- Python (建議 3.9+)

### 啟動後端 (Backend)

```bash
cd backend

# 安裝相依套件
pip install -r requirements.txt

# 啟動 FastAPI 伺服器 (開發模式)
uvicorn app:app --reload
```
預設 API 將運行在 `http://127.0.0.1:7860`。


## 📝 環境變數

需要在 `.env` 檔案中設定：
- `DOCS_USERNAME` - API 文件帳號
- `DOCS_PASSWORD` - API 文件密碼
- `FIREBASE_SECRET` - Firebase 密鑰

---

<p align="center">
  <sub>© 2026 LockerMaps. All rights reserved.</sub>
</p>
