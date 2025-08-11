import os
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from config import MODEL, check_required_envs, REQUIRED_ENV_VARS

# 檢查必要環境變數，缺少則中止
check_required_envs(REQUIRED_ENV_VARS)

root_agent = Agent(
    name="alert_query_planner",
    model=MODEL,
    description="代理程式用於分析 Graylog 警示並產生查詢策略。",
    instruction=f"""
    你是一個專業的Graylog告警分析專家。請根據graylog告警信息，分析可能的問題原因並制定查詢策略。
    需求：
    -請分析這個告警的可能原因，並制定一個系統性的查詢策略來找出根本原因。
    -請確保查詢策略是系統性的，從最可能的原因開始，逐步深入分析。
    -回覆的內容須盡量使用繁體中文。
    ***重點：
    回覆時須嚴格遵循以下JSON格式，且不可有多餘的說明：
    {{
        "event_definition_id": "告警ID",
        "event_definition_type": "告警類型",
        "event_id": "該事件本身的唯一識別碼。",
        "event_message": "告警信息",
        "analysis": "對告警原因的詳細分析",
        "timestamp_processing": "告警時間",
        "priority": 1-5的優先級（1最高，5最低）, 
        "queries": [
            {{
                "query_id": "查詢ID",
                "description": "查詢描述",
                "query": "具體的Graylog查詢語句",
                "purpose": "查詢目的",
                "time_range": "時間範圍（如：last 1 hour）",
                "time_range_start": "根據告警時間列出開始查詢時間",
                "time_range_end": "根據告警時間列出結束查詢時間",
                "expected_results": "期望的結果"
            }},...
        ], 
        "success_probability": 0.0-1.0的成功概率,
    }}
    """
)

# 創建 A2A 應用程式
host = os.environ.get("A2A_HOST", "alert-query-planner-service")
port = int(os.environ.get("PORT", 8080))
a2a_app = to_a2a(root_agent, host=host,port=port)


