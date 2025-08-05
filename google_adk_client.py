import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp

from google.cloud import aiplatform
from google.auth import default
from google.auth.transport.requests import Request

from config import Config
from models import A2AMessage, GraylogAlert, QueryStrategy, QueryPlan

logger = logging.getLogger(__name__)

class GoogleADKClient:
    """Google ADK客戶端，用於A2A通信"""
    
    def __init__(self):
        """初始化Google ADK客戶端"""
        self.config = Config()
        self._setup_adk_client()
        self.session = None
    
    def _setup_adk_client(self):
        """設置ADK客戶端"""
        try:
            # 設置認證
            credentials, project = default()
            
            # 初始化AI Platform
            aiplatform.init(
                project=self.config.GOOGLE_ADK_PROJECT_ID,
                location=self.config.GOOGLE_ADK_LOCATION,
                credentials=credentials
            )
            
            logger.info(f"Google ADK客戶端初始化成功: {self.config.GOOGLE_ADK_PROJECT_ID}")
            
        except Exception as e:
            logger.error(f"Google ADK客戶端初始化失敗: {e}")
            raise
    
    async def start_session(self):
        """啟動HTTP會話"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """關閉HTTP會話"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _convert_datetime(self, obj):
        """遞迴將 dict/list 內所有 datetime 轉成 isoformat"""
        if isinstance(obj, dict):
            return {k: self._convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetime(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    async def send_a2a_message(self, target_agent: str, message_type: str, 
                              payload: Dict[str, Any], correlation_id: Optional[str] = None) -> str:
        """發送A2A消息"""
        try:
            await self.start_session()
            message = A2AMessage(
                message_id=str(uuid.uuid4()),
                source_agent=self.config.GOOGLE_ADK_AGENT_ID,
                target_agent=target_agent,
                message_type=message_type,
                payload=payload,
                correlation_id=correlation_id
            )
            # 構建請求URL
            url = f"{self.config.GRAYLOG_SERVER_URL}{self.config.A2A_ENDPOINT}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.A2A_SECRET_KEY}",
                "X-Agent-ID": self.config.GOOGLE_ADK_AGENT_ID
            }
            message_dict = message.model_dump()
            message_dict = self._convert_datetime(message_dict)
            async with self.session.post(url, json=message_dict, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"A2A消息發送成功: {message.message_id}")
                    return message.message_id
                else:
                    error_text = await response.text()
                    logger.error(f"A2A消息發送失敗: {response.status} - {error_text}")
                    raise Exception(f"A2A消息發送失敗: {response.status}")
        except Exception as e:
            logger.error(f"發送A2A消息時發生錯誤: {e}")
            raise
        finally:
            await self.close_session()
    
    async def receive_a2a_message(self) -> Optional[A2AMessage]:
        """接收A2A消息"""
        try:
            await self.start_session()
            
            url = f"{self.config.GRAYLOG_SERVER_URL}{self.config.A2A_ENDPOINT}/receive"
            
            headers = {
                "Authorization": f"Bearer {self.config.A2A_SECRET_KEY}",
                "X-Agent-ID": self.config.GOOGLE_ADK_AGENT_ID
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    message = A2AMessage(**data)
                    logger.info(f"接收到A2A消息: {message.message_id}")
                    return message
                elif response.status == 204:
                    # 沒有消息
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"接收A2A消息失敗: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"接收A2A消息時發生錯誤: {e}")
            return None
        finally:
            await self.close_session()
    
    async def send_alert_analysis_request(self, alert: GraylogAlert, 
                                        target_agent: str = "alert-coordinator") -> str:
        """發送告警分析請求"""
        payload = {
            "request_type": "alert_analysis",
            "alert": alert.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_a2a_message(
            target_agent=target_agent,
            message_type="alert_analysis_request",
            payload=payload
        )
    
    async def send_query_strategy_response(self, strategy: QueryStrategy, 
                                         target_agent: str, 
                                         correlation_id: str) -> str:
        """發送查詢策略響應"""
        payload = {
            "response_type": "query_strategy",
            "strategy": strategy.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_a2a_message(
            target_agent=target_agent,
            message_type="query_strategy_response",
            payload=payload,
            correlation_id=correlation_id
        )
    
    async def send_query_plan_response(self, plan: QueryPlan, 
                                     target_agent: str, 
                                     correlation_id: str) -> str:
        """發送查詢計劃響應"""
        payload = {
            "response_type": "query_plan",
            "plan": plan.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_a2a_message(
            target_agent=target_agent,
            message_type="query_plan_response",
            payload=payload,
            correlation_id=correlation_id
        )
    
    async def handle_incoming_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """處理接收到的A2A消息"""
        try:
            if message.message_type == "alert_analysis_request":
                return await self._handle_alert_analysis_request(message)
            elif message.message_type == "query_strategy_request":
                return await self._handle_query_strategy_request(message)
            else:
                logger.warning(f"未知的消息類型: {message.message_type}")
                return None
                
        except Exception as e:
            logger.error(f"處理A2A消息時發生錯誤: {e}")
            return None
    
    async def _handle_alert_analysis_request(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """處理告警分析請求"""
        try:
            from ai_analyzer import AIAnalyzer
            
            # 解析告警數據
            alert_data = message.payload.get("alert", {})
            alert = GraylogAlert(**alert_data)
            
            # 使用AI分析器分析告警
            analyzer = AIAnalyzer()
            strategy = analyzer.analyze_alert(alert)
            
            # 驗證策略
            if not analyzer.validate_query_strategy(strategy):
                logger.error("生成的查詢策略驗證失敗")
                return None
            
            # 發送響應
            await self.send_query_strategy_response(
                strategy=strategy,
                target_agent=message.source_agent,
                correlation_id=message.correlation_id
            )
            
            return {
                "type": "strategy_generated",
                "strategy_id": strategy.strategy_id,
                "alert_id": alert.alert_id
            }
            
        except Exception as e:
            logger.error(f"處理告警分析請求時發生錯誤: {e}")
            return None
    
    async def _handle_query_strategy_request(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """處理查詢策略請求"""
        try:
            # 這裡可以實現更複雜的查詢策略處理邏輯
            logger.info(f"收到查詢策略請求: {message.message_id}")
            return {
                "type": "strategy_request_processed",
                "message_id": message.message_id
            }
            
        except Exception as e:
            logger.error(f"處理查詢策略請求時發生錯誤: {e}")
            return None 