# Graylog Query Planner Service

基於Python和Google ADK設計的Graylog查詢建議服務，用於自動分析告警並生成查詢策略。

## 功能特點

- 🔍 **智能告警分析**: 使用Google AI分析Graylog告警並生成查詢策略
- 🤖 **A2A通信**: 基於Google ADK實現Agent-to-Agent通信協議
- 📋 **查詢計劃管理**: 自動生成和管理系統性的查詢計劃
- 🔄 **異步處理**: 支持異步消息處理和背景任務
- 📊 **策略驗證**: 自動驗證生成的查詢策略有效性
- 🚀 **RESTful API**: 提供完整的REST API接口

## 系統架構

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Graylog       │    │   Query Planner  │    │   Google AI     │
│   Alert         │───▶│   Service        │───▶│   (Gemini Pro)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Google ADK     │
                       │   (A2A Protocol) │
                       └──────────────────┘
```

## 安裝和配置

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 環境配置

複製 `env_example.txt` 為 `.env` 並配置以下環境變量：

```bash
# Google ADK Configuration
GOOGLE_ADK_PROJECT_ID=your-project-id
GOOGLE_ADK_LOCATION=us-central1
GOOGLE_ADK_AGENT_ID=graylog-query-planner

# AI Configuration
GOOGLE_AI_API_KEY=your-google-ai-api-key
GOOGLE_AI_MODEL=gemini-pro

# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000

# Graylog Configuration
GRAYLOG_SERVER_URL=http://localhost:9000
GRAYLOG_API_TOKEN=your-graylog-api-token

# A2A Communication Configuration
A2A_ENDPOINT=/api/v1/a2a
A2A_SECRET_KEY=your-secret-key

# Logging Configuration
LOG_LEVEL=INFO
```

### 3. 啟動服務

```bash
python main.py
```

服務將在 `http://localhost:8000` 啟動，API文檔可在 `http://localhost:8000/docs` 查看。

## API 接口

### 核心功能

#### 1. 分析告警
```http
POST /api/v1/analyze-alert
Content-Type: application/json

{
  "alert": {
    "alert_id": "alert_001",
    "timestamp": "2024-01-01T12:00:00",
    "severity": "high",
    "source": "web-server-01",
    "message": "HTTP 500 error rate exceeded threshold",
    "details": {
      "error_count": 150,
      "threshold": 100
    },
    "tags": ["http", "error"],
    "environment": "production",
    "service": "user-service"
  }
}
```

#### 2. 創建查詢計劃
```http
POST /api/v1/create-plan
Content-Type: application/json

{
  "alert": {
    // 告警信息
  },
  "strategy": {
    // 可選的查詢策略
  }
}
```

#### 3. 管理查詢計劃
```http
GET    /api/v1/plans                    # 列出所有計劃
GET    /api/v1/plans/{plan_id}         # 獲取特定計劃
PUT    /api/v1/plans/{plan_id}/status  # 更新計劃狀態
DELETE /api/v1/plans/{plan_id}         # 刪除計劃
```

### A2A 通信

#### 1. 處理A2A消息
```http
POST /api/v1/a2a
Content-Type: application/json

{
  "message": {
    "message_id": "msg_001",
    "source_agent": "alert-coordinator",
    "target_agent": "graylog-query-planner",
    "message_type": "alert_analysis_request",
    "payload": {
      "alert": {
        // 告警信息
      }
    }
  }
}
```

#### 2. 發送A2A消息
```http
POST /api/v1/a2a/send?target_agent=alert-coordinator&message_type=query_strategy_response
Content-Type: application/json

{
  "strategy": {
    // 查詢策略
  }
}
```

## 數據模型

### GraylogAlert
```python
{
  "alert_id": "唯一標識符",
  "timestamp": "告警時間",
  "severity": "告警嚴重程度 (low/medium/high/critical)",
  "source": "告警來源",
  "message": "告警訊息",
  "details": "詳細信息",
  "tags": ["標籤列表"],
  "environment": "環境信息",
  "service": "服務名稱"
}
```

### QueryStrategy
```python
{
  "strategy_id": "策略唯一標識符",
  "alert_id": "關聯的告警ID",
  "analysis": "AI分析的告警原因",
  "queries": [
    {
      "query_id": "查詢唯一標識符",
      "description": "查詢描述",
      "query": "具體的Graylog查詢語句",
      "purpose": "查詢目的",
      "time_range": "時間範圍",
      "expected_results": "期望的結果類型"
    }
  ],
  "priority": "優先級 (1-5)",
  "estimated_time": "預估執行時間（分鐘）",
  "success_probability": "成功概率 (0.0-1.0)"
}
```

## 使用示例

### 1. 基本使用

```python
import asyncio
from models import GraylogAlert, AlertSeverity
from ai_analyzer import AIAnalyzer
from query_planner import QueryPlanner

# 創建告警
alert = GraylogAlert(
    alert_id="alert_001",
    timestamp=datetime.now(),
    severity=AlertSeverity.HIGH,
    source="web-server-01",
    message="HTTP 500 error rate exceeded threshold",
    details={"error_count": 150, "threshold": 100},
    tags=["http", "error"],
    environment="production",
    service="user-service"
)

# 分析告警
analyzer = AIAnalyzer()
strategy = analyzer.analyze_alert(alert)

# 創建查詢計劃
planner = QueryPlanner()
plan = planner.create_query_plan(alert, strategy)
```

### 2. A2A通信示例

```python
from google_adk_client import GoogleADKClient

async def example_a2a():
    client = GoogleADKClient()
    
    # 發送告警分析請求
    message_id = await client.send_alert_analysis_request(
        alert=alert,
        target_agent="alert-coordinator"
    )
    
    # 接收響應
    message = await client.receive_a2a_message()
    if message:
        print(f"收到響應: {message.payload}")
    
    await client.close_session()
```

## 測試

運行測試示例：

```bash
python test_example.py
```

## 部署

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graylog-query-planner
spec:
  replicas: 2
  selector:
    matchLabels:
      app: graylog-query-planner
  template:
    metadata:
      labels:
        app: graylog-query-planner
    spec:
      containers:
      - name: query-planner
        image: graylog-query-planner:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_AI_API_KEY
          valueFrom:
            secretKeyRef:
              name: google-ai-secret
              key: api-key
```

## 開發指南

### 項目結構

```
alert-query-planner/
├── main.py                 # 主服務文件
├── config.py              # 配置文件
├── models.py              # 數據模型
├── ai_analyzer.py         # AI分析器
├── google_adk_client.py   # Google ADK客戶端
├── query_planner.py       # 查詢計劃器
├── test_example.py        # 測試示例
├── requirements.txt       # 依賴文件
├── env_example.txt       # 環境變量示例
└── README.md             # 項目文檔
```

### 擴展功能

1. **自定義AI模型**: 修改 `ai_analyzer.py` 中的提示模板
2. **添加新的查詢類型**: 在 `models.py` 中擴展查詢策略模型
3. **實現更多A2A協議**: 在 `google_adk_client.py` 中添加新的消息處理器
4. **優化查詢計劃**: 在 `query_planner.py` 中實現更複雜的優化算法

## 故障排除

### 常見問題

1. **AI API密鑰錯誤**: 確保 `GOOGLE_AI_API_KEY` 正確設置
2. **ADK連接失敗**: 檢查Google ADK項目配置和認證
3. **A2A通信失敗**: 驗證A2A端點和密鑰配置
4. **查詢策略驗證失敗**: 檢查AI生成的策略格式是否符合要求

### 日誌調試

設置 `LOG_LEVEL=DEBUG` 來獲取詳細的調試信息。

## 貢獻

歡迎提交Issue和Pull Request來改進這個項目。

## 許可證

MIT License