# LDS — 管線洩漏監測系統

單管線洩漏監測 MVP：模擬感測資料、三種偵測演算法、即時儀表板與歷史查詢。

規格：[docs/superpowers/specs/2026-10-30-lds-design.md](docs/superpowers/specs/2026-10-30-lds-design.md)

## 目錄

| 路徑 | 說明 |
|------|------|
| `backend/` | FastAPI（uv 虛擬環境 `.venv`） |
| `frontend/` | Nuxt + Ant Design Vue + Plotly.js |
| `data/` | SQLite（`lds.db`，不進版控） |
| `docs/` | 規格與計畫 |

## 需求

- Python 3.9+、[uv](https://github.com/astral-sh/uv)
- Node.js 18+、npm

## 啟動後端

```bash
cd backend
source .venv/bin/activate
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API 文件：http://127.0.0.1:8000/docs

## 啟動前端

```bash
cd frontend
npm install
npm run dev
```

預設：http://127.0.0.1:3000  
後端位址可用環境變數覆寫：`NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000`

## 示範洩漏

1. 開啟即時監測頁
2. 將「洩漏注入」切為 ON
3. 觀察流量／壓力偏移、監測狀態變為「觀察」或「告警」、三種演算法結果更新
4. 「輸送運行」可切換「輸送中／停輸」

## 測試（後端）

```bash
cd backend
uv run pytest -v
```
