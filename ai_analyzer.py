import logging
import uuid
from config import Config
from models import GraylogAlert, QueryStrategy
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

logger = logging.getLogger(__name__)

# 依官方ADK範例初始化Agent
root_agent = Agent(
    name="graylog_query_agent",
    model=Config.GOOGLE_AI_MODEL,  # 可根據需求調整
    description="Agent to analyze Graylog alerts and generate query strategies.",
    instruction="You are an expert in analyzing Graylog alerts and generating systematic query strategies.",
    tools=[],  # 如有自定義工具可加在這裡
)

class AIAnalyzer:
    """AI分析器，用於分析Graylog告警並生成查詢策略"""
    def __init__(
        self,
        user_id: str = 'user',
        app_name: str = 'graylog_query_agent',
    ):
        self.session_service = InMemorySessionService()
        self.session = None
        self.app_name = app_name
        self.user_id = user_id

    async def analyze_alert(self, alert: GraylogAlert) -> QueryStrategy:
        try:
            session = await self.session_service.create_session(
                app_name="graylog_query_agent",
                user_id="user"
            )
            runner = Runner(
                agent=root_agent,
                app_name=self.app_name,
                session_service=self.session_service,
            )
            prompt = self._build_analysis_prompt(alert)
            part_obj = Part(text=prompt)
            content = Content(role="user", parts=[part_obj])
            response_text = ""
            async for event in runner.run_async(
                user_id=session.user_id, session_id=session.id, new_message=content
            ):
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break
            strategy_data = self._parse_ai_response(str(response_text))
            strategy = QueryStrategy(
                strategy_id=str(uuid.uuid4()),
                alert_id=alert.alert_id,
                analysis=strategy_data.get("analysis", ""),
                queries=strategy_data.get("queries", []),
                priority=strategy_data.get("priority", 1),
                estimated_time=strategy_data.get("estimated_time", 30),
                success_probability=strategy_data.get("success_probability", 0.5)
            )
            logger.info(f"成功生成查詢策略: {strategy.strategy_id}")
            return strategy
        except Exception as e:
            logger.error(f"分析告警失敗: {e}")
            raise

    def _build_analysis_prompt(self, alert: GraylogAlert) -> str:
        prompt = f"""
你是一個專業的Graylog告警分析專家。請根據以下告警信息，分析可能的問題原因並制定查詢策略。
告警信息：
- 告警ID: {alert.alert_id}
- 時間: {alert.timestamp}
- 嚴重程度: {alert.severity}
- 來源: {alert.source}
- 訊息: {alert.message}
- 環境: {alert.environment}
- 服務: {alert.service}
- 標籤: {', '.join(alert.tags)}
- 詳細信息: {alert.details}
請分析這個告警的可能原因，並制定一個系統性的查詢策略來找出根本原因。
請以JSON格式返回結果，包含以下字段：
{{
    "analysis": "對告警原因的詳細分析",
    "queries": [
        {{
            "query_id": "查詢唯一標識符",
            "description": "查詢描述",
            "query": "具體的Graylog查詢語句",
            "purpose": "查詢目的",
            "time_range": "時間範圍（如：last 1 hour）",
            "time_range_start": "根據告警時間列出開始查詢時間",
            "time_range_end": "根據告警時間列出結束查詢時間",
            "expected_results": "期望的結果類型"
        }}
    ],
    "priority": 1-5的優先級（1最高，5最低）, 
    "estimated_time": 預估執行時間（分鐘）, 
    "success_probability": 0.0-1.0的成功概率
}}
請確保查詢策略是系統性的，從最可能的原因開始，逐步深入分析。
回傳時以繁體中文回答。
"""
        return prompt

    def _parse_ai_response(self, response_text: str):
        import json
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("無法解析AI響應為JSON格式，使用默認響應")
                return {
                    "analysis": "無法分析告警原因",
                    "queries": [],
                    "priority": 3,
                    "estimated_time": 30,
                    "success_probability": 0.3
                }
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失敗: {e}")
            return {
                "analysis": "AI響應解析失敗",
                "queries": [],
                "priority": 3,
                "estimated_time": 30,
                "success_probability": 0.3
            }

    def validate_query_strategy(self, strategy: QueryStrategy) -> bool:
        try:
            if not strategy.analysis or len(strategy.analysis.strip()) == 0:
                return False
            if not strategy.queries or len(strategy.queries) == 0:
                return False
            for query in strategy.queries:
                required_fields = ["query_id", "description", "query", "purpose"]
                for field in required_fields:
                    if field not in query or not query[field]:
                        return False
            if not (1 <= strategy.priority <= 5):
                return False
            if not (0.0 <= strategy.success_probability <= 1.0):
                return False
            if strategy.estimated_time <= 0:
                return False
            return True
        except Exception as e:
            logger.error(f"策略驗證失敗: {e}")
            return False