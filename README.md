# Alert Query Planner (A2A)

一個專業的 Graylog 警示分析代理程式，基於 Google Agent Development Kit (ADK) 和 Agent-to-Agent (A2A) 架構開發。該系統能夠自動分析 Graylog 警示訊息並產生系統性的查詢策略，協助運維人員快速定位和解決問題。

## 🌟 主要功能

- **智能警示分析**: 使用 Gemini 2.0 Flash 模型分析 Graylog 警示訊息
- **自動查詢規劃**: 根據警示內容生成系統性的查詢策略
- **產生查詢語法**: 根據查詢規劃產生查詢語法
- **優先級評估**: 自動評估問題的優先級（1-5級）
- **時間範圍優化**: 智能計算查詢的時間範圍
- **成功率預測**: 評估查詢策略的成功概率
- **A2A 架構**: 支援 Agent-to-Agent 通訊協定

## 🏗️ 系統架構

```
alert-query-planner/
├── agent/
│   ├── __init__.py
│   └── agent.py          # 主要代理程式邏輯
├── config.py             # 配置管理
├── requirements.txt      # Python 依賴
├── dockerfile           # Docker 配置
└── README.md            # 說明文件
```

## 🚀 快速開始

### 環境需求

- Python 3.13+
- Google ADK SDK
- A2A SDK

### 本地開發

1. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數**
   ```bash
   # Windows PowerShell
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=cloud-sre-poc-465509
    GOOGLE_CLOUD_LOCATION=us-central1
    GOOGLE_APPLICATION_CREDENTIALS=
    MODEL="gemini-2.0-flash"
   ```

3. **啟動服務**
   ```bash
   python -m uvicorn agent.agent:a2a_app --host 0.0.0.0 --port 8080
   ```

### Docker 部署

1. **建置 Docker 映像**
   ```bash
   docker build -t alert-query-planner .
   ```

2. **運行容器**
   ```bash
   docker run -d -p 8001:8001 -e MODEL=gemini-2.0-flash --name alert-query-planner alert-query-planner
   ```

## 📝 API 使用方式

### 輸入格式
```json
{
  "event_definition_id": "5f8d8c1013a7e34dc27db450",
  "event_definition_type": "aggregation",
  "event_title": "防火牆多次登入失敗告警",
  "event_definition_description": "同一 IP 在 5 分鐘內登入失敗次數超過 10 次",
  "job_definition_id": "5f8d8c1313a7e34dc27db451",
  "event_id": "5f8d8c2313a7e34dc27db452",
  "event_origin_context": "graylog",
  "event_timestamp_processing": "2025-08-06T02:57:00.000Z",
  "event_timerange_start": "2025-08-06T02:52:00.000Z",
  "event_timerange_end": "2025-08-06T02:57:00.000Z",
  "event_streams": "stream-id-1",
  "event_source_streams": "firewall-logs-stream",
  "event_alert": true,
  "event_message": "IP 192.168.1.100 在 5 分鐘內登入失敗 12 次",
  "event_source": "firewall01",
  "event_key": "192.168.1.100",
  "event_priority": 2,
  "backlog": [
    {
      "id": "msgid-001",
      "message": "登入失敗，使用者：admin，來源：192.168.1.100"
    },
    {
      "id": "msgid-002",
      "message": "登入失敗，使用者：admin，來源：192.168.1.100"
    }
  ]
}
```

### 輸出格式

代理程式會返回結構化的分析結果：

```json
{
  "event_definition_id": "告警ID",
  "event_definition_type": "告警類型",
  "event_id": "事件唯一識別碼",
  "event_message": "告警信息",
  "analysis": "對告警原因的詳細分析",
  "timestamp_processing": "告警時間",
  "priority": "1-5的優先級（1最高，5最低）",
  "queries": [
    {
      "query_id": "query_001",
      "description": "查詢描述",
      "query": "具體的Graylog查詢語句",
      "purpose": "查詢目的",
      "time_range": "last 1 hour",
      "time_range_start": "2025-08-08T09:00:00Z",
      "time_range_end": "2025-08-08T10:00:00Z",
      "expected_results": "期望的結果"
    }
  ],
  "success_probability": "0.0-1.0的成功概率"
}
```

## ⚙️ 配置選項

### 環境變數

| 變數名稱 | 預設值 | 必需 | 說明 |
|---------|--------|------|------|
| `MODEL` | `gemini-2.0-flash` | ✅ | 使用的 AI 模型 |
| `PYTHONPATH` | `/app` | ❌ | Python 路徑 |
| `PYTHONUNBUFFERED` | `1` | ❌ | Python 輸出緩衝設定 |

## 🔧 開發指南

### 專案結構說明

- **`config.py`**: 環境變數管理和配置驗證
- **`agent/agent.py`**: 核心代理程式邏輯，包含 Graylog 警示分析指令
- **`dockerfile`**: Docker 容器化配置
- **`requirements.txt`**: Python 依賴套件清單

### 擴展功能

要擴展代理程式的功能，可以修改 `agent/agent.py` 中的 `instruction` 部分，調整分析邏輯或輸出格式。

## 📊 監控與維護

### 健康檢查

系統內建健康檢查端點，每 30 秒檢查一次：

```bash
curl -f http://localhost:8001/ || exit 1
```

### 日誌監控

查看容器日誌：

```bash
docker logs alert-query-planner
```