# 管線洩漏監測系統（LDS）設計規格

**日期：** 2026-10-30  
**狀態：** Approved for MVP implementation

## 目標

建立可本機運行的單管線洩漏監測 MVP：以模擬感測資料驅動三種偵測模式，並在前端呈現即時儀表板與歷史查詢。

## 決策摘要

| 項目 | 決定 |
|------|------|
| 產品 | 單管線洩漏監測 |
| 資料來源 | 後端模擬感測器資料 |
| 模式 | 準即時輪詢 + 歷史區間查詢 |
| 認證 | 無 |
| 架構 | Nuxt / Ant Design Vue / Plotly.js ↔ FastAPI ↔ SQLite |
| 後端環境 | `backend/` 以 uv 管理虛擬環境（`.venv`）與依賴（`pyproject.toml` + `uv.lock`） |
| CORS | `allow_origins=["*"]` |
| 演算法 | 壓力梯度、流量變化量、壓力波（簡化、可擴充） |

## 系統架構

```
frontend (Nuxt) --poll/REST--> backend (FastAPI)
                                    |
                              background simulator
                                    |
                              SQLite (data/lds.db)
```

- `frontend/`：即時監測頁、歷史查詢頁
- `backend/`：REST API、背景模擬器、洩漏演算法
- `docs/`：規格與計畫
- `data/`：SQLite 檔案目錄（DB 檔不進版控）

## 狀態模型（兩軸）

1. **輸送狀態：** `輸送中` | `停輸`（由模擬器 `transport_running` 控制；停輸時流量接近 0）
2. **洩漏監測：** `正常` | `觀察` | `告警`（由三種演算法結果彙總）

狀態摘要另顯示：內容物種類、最新壓力／流量／溫度。

## 資料模型（SQLite）

### pipeline

靜態管線參數：`name`, `length_m`, `diameter_m`, `content_type`

### sensor_reading

時間序列：`ts`, `pressure_in`, `pressure_out`, `flow_in`, `flow_out`, `temperature`

### detection_result

各演算法輸出：`ts`, `method`, `leak_suspected`, `severity`, `metrics_json`

### sim_state

模擬控制：`leak_injected` (bool), `transport_running` (bool)

## 模擬器行為

- 每隔 N 秒寫入一筆 `sensor_reading`（含小噪音）
- `transport_running=false`：流量近 0
- `leak_injected=true`：進出口流量失衡與壓力偏移，供演算法觸發
- 同一張 `sensor_reading` 支援歷史區間查詢

## 洩漏演算法（MVP 簡化）

1. **壓力梯度法：** 實際 ΔP／距離 vs 理論梯度，偏差超閾值 → 可疑
2. **流量變化量：** 進出口流量差與變化率，失衡超閾值 → 可疑
3. **壓力波（簡化）：** 短時間壓力突變特徵 → 可疑事件

彙總規則（MVP）：任一路 `alarm` 級 → 告警；否則任一路可疑 → 觀察；否則正常。

## API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/health` | 健康檢查 |
| GET | `/api/pipeline` | 管線靜態資訊 |
| GET | `/api/readings/latest?limit=` | 最近 N 筆讀數 |
| GET | `/api/readings?from=&to=` | 歷史區間讀數 |
| GET | `/api/status` | 輸送／監測狀態、最新讀數、變化率、各方法結果 |
| GET | `/api/detections?from=&to=` | 歷史偵測結果 |
| POST | `/api/sim/leak` | `{ "enabled": bool }` 洩漏注入 |
| POST | `/api/sim/transport` | `{ "running": bool }` 輸送開關 |

## 前端

### 即時監測（首頁）

- 狀態摘要（兩軸 + 內容物 + 最新 P/Q/T）
- Plotly：流量趨勢、壓力趨勢（進出口）
- 變化率卡片
- 三種演算法結果並列
- 模擬控制（洩漏注入、輸送開關）
- 輪詢約 2–3 秒；失敗時 AntDV message，保留上次圖資料

### 歷史查詢

- 時間區間選擇 → 趨勢圖 + 偵測紀錄表

## 錯誤處理

- API 失敗：前端提示，不清空上次成功資料
- 模擬器寫入失敗：記 log，不拖垮 API 行程

## 非目標（本 MVP 不做）

- 登入／權限
- 多管線
- 真實 SCADA／感測器接入
- 工業級物理精度演算
