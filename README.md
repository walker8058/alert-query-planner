# Alert Query Planner (A2A)

一個專業的 Graylog 警示分析代理程式，基於 Google Agent Development Kit (ADK) 和 Agent-to-Agent (A2A) 架構開發。該系統能夠自動分析 Graylog 警示訊息並產生系統性的查詢策略，協助運維人員快速定位和解決問題。

## 🌟 主要功能

- **智能警示分析**: 使用 Gemini 2.0 Flash 模型分析 Graylog 警示訊息
- **自動查詢規劃**: 根據警示內容選擇查詢策略
- **時間範圍優化**: 智能計算查詢的時間範圍
- **A2A 架構**: 支援 Agent-to-Agent 通訊協定

## 🏗️ 系統架構

```
alert-query-planner/
├── agent/
│   ├── __init__.py
│   ├── agent.py          # 主要代理程式邏輯
│   └── time_tool.py      # 獲取目前時間
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
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=cloud-sre-poc-465509
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=
   MODEL=gemini-2.5-pro
   A1_TIME_RANGE=last 20 minutes
   A2_TIME_RANGE=last 10 minutes
   A2A_HOST=127.0.0.1
   A2A_PORT=8080

3. **啟動服務**
   ```bash
   python -m uvicorn agent.agent:a2a_app --host 0.0.0.0 --port 8080
   ```

4. **查看agent card**
   http://127.0.0.1:8080/.well-known/agent-card.json

### Docker 部署

1. **建置 Docker 映像**
   ```bash
   docker build -t alert-query-planner .
   ```

2. **運行容器**
   ```bash
   docker run -d -p 8001:8001 -e MODEL=gemini-2.5-pro --name alert-query-planner alert-query-planner
   ```

## 📝 API 使用方式

### 輸入格式
{
  "event_id": "event-001",
  "event_title": "Business Routing Alert",
  "event_description": "msp-svc-businessrouting 服務發生警示事件",
  "event_priority": "HIGH",
  "event_timestamp": "2025-08-11T06:20:16.771Z",
  "backlog": [
    {
      "發生時間": "2025-08-11T06:20:16.771Z",
      "訊息大小": "1372",
      "雲類型": "epaas",
      "專案名稱": "midlxmsp01",
      "容器鏡像檔": "parhnchar01.nc.aaa.intra.uwccb/midlxmsp01/msp-svc-businessrouting:20240918.1",
      "容器名稱": "msp-svc-businessrouting",
      "服務名稱": "msp-svc-businessrouting-5c68cb64c-fxhdp",
      "訊息來源": "parhepaasocp4n11.aaa.intra.uwccb",
      "警示訊息內容": "2025-08-11T06:20:16.760035927+00:00 stdout F 2025-08-11 14:20:16,759 INFO [executor-thread-484460hread] cub.msp.svc.businessrouting.process.OutputLogProcessor.loggerCompletedWithSpendTime(OutputLogProcessor.java:47) [ROUTING]COMPLETE[S][FNSCIF0064][MID-NT-STK-01][85051867787115816620][6531f06260094b198d97][MSP-C-FAVORTWDQ001][MW99][30043]{"TRANRS":{"MsgNo":"123654789","CycleNo":"123456789","TxnCode":"987654321"},"MWHEADER":{"O360SEQ":"20030402962323565673","RETURNDESC":"Benkend Timeout!","TXNSEQ":"6531f06260094b198d97","RETURNCODE":"MW99","RETURNCODECHANNEL":"","SOURCECHANNEL":"MID-NT-STK-01","MSGID":"FNSCIF0064"}}"
    }
  ]
}

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