import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json

from config import Config
from models import GraylogAlert, QueryStrategy, QueryPlan, A2AMessage
from ai_analyzer import AIAnalyzer
from google_adk_client import GoogleADKClient
from query_planner import QueryPlanner

# 配置日誌
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建FastAPI應用
app = FastAPI(
    title="Graylog Query Planner Service",
    description="基於Google ADK的Graylog查詢建議服務",
    version="1.0.0"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局變量
ai_analyzer = None
adk_client = None
query_planner = None

class AlertRequest(BaseModel):
    """告警請求模型"""
    alert: GraylogAlert

class QueryPlanRequest(BaseModel):
    """查詢計劃請求模型"""
    alert: GraylogAlert
    strategy: Optional[QueryStrategy] = None

class A2AMessageRequest(BaseModel):
    """A2A消息請求模型"""
    message: A2AMessage

@app.on_event("startup")
async def startup_event():
    """服務啟動事件"""
    global ai_analyzer, adk_client, query_planner
    
    try:
        # 初始化組件
        ai_analyzer = AIAnalyzer()
        adk_client = GoogleADKClient()
        query_planner = QueryPlanner()
        
        logger.info("服務啟動成功")
        
    except Exception as e:
        logger.error(f"服務啟動失敗: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """服務關閉事件"""
    try:
        if adk_client:
            await adk_client.close_session()
        logger.info("服務關閉成功")
    except Exception as e:
        logger.error(f"服務關閉時發生錯誤: {e}")

@app.get("/")
async def root():
    """根路徑"""
    return {
        "service": "Graylog Query Planner Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "components": {
            "ai_analyzer": ai_analyzer is not None,
            "adk_client": adk_client is not None,
            "query_planner": query_planner is not None
        }
    }

@app.post("/api/v1/analyze-alert")
async def analyze_alert(request: AlertRequest):
    """分析告警並生成查詢策略"""
    try:
        if not ai_analyzer:
            raise HTTPException(status_code=500, detail="AI分析器未初始化")
        
        # 使用AI分析告警
        strategy = ai_analyzer.analyze_alert(request.alert)
        
        # 驗證策略
        if not ai_analyzer.validate_query_strategy(strategy):
            raise HTTPException(status_code=400, detail="生成的查詢策略驗證失敗")
        
        logger.info(f"成功分析告警: {request.alert.alert_id}")
        
        return {
            "success": True,
            "strategy": strategy.model_dump(),
            "alert_id": request.alert.alert_id
        }
        
    except Exception as e:
        logger.error(f"分析告警失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/create-plan")
async def create_query_plan(request: QueryPlanRequest):
    """創建查詢計劃"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        # 如果沒有提供策略，使用AI生成
        if not request.strategy:
            if not ai_analyzer:
                raise HTTPException(status_code=500, detail="AI分析器未初始化")
            request.strategy = ai_analyzer.analyze_alert(request.alert)
        
        # 創建查詢計劃
        plan = query_planner.create_query_plan(request.alert, request.strategy)
        
        logger.info(f"成功創建查詢計劃: {plan.plan_id}")
        
        return {
            "success": True,
            "plan": plan.model_dump(),
            "plan_id": plan.plan_id
        }
        
    except Exception as e:
        logger.error(f"創建查詢計劃失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/plans")
async def list_plans():
    """列出所有查詢計劃"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        plans = query_planner.list_all_plans()
        
        return {
            "success": True,
            "plans": plans,
            "total": len(plans)
        }
        
    except Exception as e:
        logger.error(f"列出計劃失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/plans/{plan_id}")
async def get_plan(plan_id: str):
    """獲取特定查詢計劃"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        plan = query_planner.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="計劃不存在")
        
        return {
            "success": True,
            "plan": plan.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取計劃失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/plans/{plan_id}/status")
async def update_plan_status(plan_id: str, status: str):
    """更新計劃狀態"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        success = query_planner.update_plan_status(plan_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="計劃不存在")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新計劃狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/plans/{plan_id}")
async def delete_plan(plan_id: str):
    """刪除查詢計劃"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        success = query_planner.delete_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="計劃不存在")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "message": "計劃已刪除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除計劃失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/a2a")
async def handle_a2a_message(request: A2AMessageRequest):
    """處理A2A消息"""
    try:
        if not adk_client:
            raise HTTPException(status_code=500, detail="ADK客戶端未初始化")
        
        # 處理A2A消息
        result = await adk_client.handle_incoming_message(request.message)
        
        if result:
            return {
                "success": True,
                "result": result,
                "message_id": request.message.message_id
            }
        else:
            return {
                "success": False,
                "message": "無法處理A2A消息",
                "message_id": request.message.message_id
            }
        
    except Exception as e:
        logger.error(f"處理A2A消息失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/a2a/send")
async def send_a2a_message(target_agent: str, message_type: str, payload: Dict[str, Any]):
    """發送A2A消息"""
    try:
        if not adk_client:
            raise HTTPException(status_code=500, detail="ADK客戶端未初始化")
        
        message_id = await adk_client.send_a2a_message(
            target_agent=target_agent,
            message_type=message_type,
            payload=payload
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "target_agent": target_agent
        }
        
    except Exception as e:
        logger.error(f"發送A2A消息失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/a2a/receive")
async def receive_a2a_message():
    """接收A2A消息"""
    try:
        if not adk_client:
            raise HTTPException(status_code=500, detail="ADK客戶端未初始化")
        
        message = await adk_client.receive_a2a_message()
        
        if message:
            return {
                "success": True,
                "message": message.model_dump()
            }
        else:
            return {
                "success": True,
                "message": None
            }
        
    except Exception as e:
        logger.error(f"接收A2A消息失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/validate-plan/{plan_id}")
async def validate_plan(plan_id: str):
    """驗證查詢計劃"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        validation_result = query_planner.validate_plan(plan_id)
        
        return {
            "success": True,
            "plan_id": plan_id,
            "validation": validation_result
        }
        
    except Exception as e:
        logger.error(f"驗證計劃失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/optimize-plan/{plan_id}")
async def optimize_plan(plan_id: str):
    """優化查詢計劃"""
    try:
        if not query_planner:
            raise HTTPException(status_code=500, detail="查詢計劃器未初始化")
        
        optimized_plan = query_planner.optimize_plan(plan_id)
        
        if optimized_plan:
            return {
                "success": True,
                "plan": optimized_plan.model_dump(),
                "plan_id": plan_id
            }
        else:
            raise HTTPException(status_code=404, detail="計劃不存在或優化失敗")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"優化計劃失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 背景任務：定期檢查A2A消息
async def background_a2a_checker():
    """背景A2A消息檢查器"""
    while True:
        try:
            if adk_client:
                message = await adk_client.receive_a2a_message()
                if message:
                    logger.info(f"背景處理A2A消息: {message.message_id}")
                    await adk_client.handle_incoming_message(message)
        except Exception as e:
            logger.error(f"背景A2A檢查失敗: {e}")
        
        # 等待30秒後再次檢查
        await asyncio.sleep(30)

@app.on_event("startup")
async def start_background_tasks():
    """啟動背景任務"""
    asyncio.create_task(background_a2a_checker())

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.SERVICE_HOST,
        port=Config.SERVICE_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    ) 