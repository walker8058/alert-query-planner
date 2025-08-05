from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GraylogAlert(BaseModel):
    """Graylog告警數據模型"""
    alert_id: str = Field(..., description="告警唯一標識符")
    timestamp: datetime = Field(..., description="告警時間戳")
    severity: AlertSeverity = Field(..., description="告警嚴重程度")
    source: str = Field(..., description="告警來源")
    message: str = Field(..., description="告警訊息")
    details: Dict[str, Any] = Field(default_factory=dict, description="告警詳細信息")
    tags: List[str] = Field(default_factory=list, description="告警標籤")
    environment: str = Field(..., description="環境信息")
    service: str = Field(..., description="服務名稱")

class QueryStrategy(BaseModel):
    """查詢策略數據模型"""
    strategy_id: str = Field(..., description="策略唯一標識符")
    alert_id: str = Field(..., description="關聯的告警ID")
    analysis: str = Field(..., description="AI分析的告警原因")
    queries: List[Dict[str, Any]] = Field(..., description="建議的查詢列表")
    priority: int = Field(..., description="查詢優先級")
    estimated_time: int = Field(..., description="預估執行時間（分鐘）")
    success_probability: float = Field(..., description="成功概率（0-1）")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")

class A2AMessage(BaseModel):
    """A2A通信消息模型"""
    message_id: str = Field(..., description="消息唯一標識符")
    source_agent: str = Field(..., description="發送方代理")
    target_agent: str = Field(..., description="接收方代理")
    message_type: str = Field(..., description="消息類型")
    payload: Dict[str, Any] = Field(..., description="消息內容")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳")
    correlation_id: Optional[str] = Field(None, description="關聯ID")

class QueryPlan(BaseModel):
    """查詢計劃數據模型"""
    plan_id: str = Field(..., description="計劃唯一標識符")
    alert: GraylogAlert = Field(..., description="原始告警")
    strategy: QueryStrategy = Field(..., description="查詢策略")
    status: str = Field(default="pending", description="計劃狀態")
    execution_order: List[str] = Field(..., description="執行順序")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="依賴關係")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間") 