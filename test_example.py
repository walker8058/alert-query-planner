#!/usr/bin/env python3
"""
Graylog Query Planner Service 測試示例
"""

import asyncio
import json
from datetime import datetime
from models import GraylogAlert, AlertSeverity
from ai_analyzer import AIAnalyzer
from query_planner import QueryPlanner

def create_sample_alert():
    """創建示例告警"""
    return GraylogAlert(
        alert_id="alert_001",
        timestamp=datetime.now(),
        severity=AlertSeverity.HIGH,
        source="web-server-01",
        message="HTTP 500 error rate exceeded threshold",
        details={
            "error_count": 150,
            "threshold": 100,
            "time_window": "5 minutes",
            "endpoint": "/api/users"
        },
        tags=["http", "error", "web-server"],
        environment="production",
        service="user-service"
    )

def create_database_alert():
    """創建數據庫告警示例"""
    return GraylogAlert(
        alert_id="alert_002",
        timestamp=datetime.now(),
        severity=AlertSeverity.CRITICAL,
        source="database-server-01",
        message="Database connection pool exhausted",
        details={
            "active_connections": 100,
            "max_connections": 100,
            "waiting_connections": 25,
            "database": "user_db"
        },
        tags=["database", "connection", "pool"],
        environment="production",
        service="database-service"
    )

async def test_ai_analyzer():
    """測試AI分析器"""
    print("=== 測試AI分析器 ===")
    
    try:
        analyzer = AIAnalyzer()
        
        # 測試Web服務器告警
        web_alert = create_sample_alert()
        print(f"分析告警: {web_alert.alert_id}")
        print(f"告警訊息: {web_alert.message}")
        
        strategy = await analyzer.analyze_alert(web_alert)
        
        print(f"生成的策略ID: {strategy.strategy_id}")
        print(f"分析結果: {strategy.analysis}")
        print(f"查詢數量: {len(strategy.queries)}")
        print(f"優先級: {strategy.priority}")
        print(f"預估時間: {strategy.estimated_time}分鐘")
        print(f"成功概率: {strategy.success_probability}")
        
        # 驗證策略
        is_valid = analyzer.validate_query_strategy(strategy)
        print(f"策略驗證結果: {'通過' if is_valid else '失敗'}")
        
        return strategy
        
    except Exception as e:
        print(f"AI分析器測試失敗: {e}")
        return None

async def test_query_planner():
    """測試查詢計劃器"""
    print("\n=== 測試查詢計劃器 ===")
    
    try:
        planner = QueryPlanner()
        
        # 創建告警和策略
        alert = create_database_alert()
        analyzer = AIAnalyzer()
        strategy = await analyzer.analyze_alert(alert)
        
        # 創建查詢計劃
        plan = planner.create_query_plan(alert, strategy)
        
        print(f"計劃ID: {plan.plan_id}")
        print(f"計劃狀態: {plan.status}")
        print(f"執行順序: {plan.execution_order}")
        print(f"依賴關係: {plan.dependencies}")
        
        # 獲取計劃摘要
        summary = planner.get_plan_summary(plan.plan_id)
        print(f"計劃摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
        
        # 驗證計劃
        validation = planner.validate_plan(plan.plan_id)
        print(f"計劃驗證結果: {json.dumps(validation, indent=2, ensure_ascii=False)}")
        
        return plan
        
    except Exception as e:
        print(f"查詢計劃器測試失敗: {e}")
        return None

async def test_a2a_communication():
    """測試A2A通信"""
    print("\n=== 測試A2A通信 ===")
    
    try:
        from google_adk_client import GoogleADKClient
        
        client = GoogleADKClient()
        
        # 創建示例告警
        alert = create_sample_alert()
        
        # 發送告警分析請求
        message_id = await client.send_alert_analysis_request(
            alert=alert,
            target_agent="alert-coordinator"
        )
        
        print(f"發送A2A消息成功: {message_id}")
        
        # 接收消息
        message = await client.receive_a2a_message()
        if message:
            print(f"接收到A2A消息: {message.message_id}")
            print(f"消息類型: {message.message_type}")
        else:
            print("沒有接收到A2A消息")
        
        await client.close_session()
        
    except Exception as e:
        print(f"A2A通信測試失敗: {e}")

def test_models():
    """測試數據模型"""
    print("\n=== 測試數據模型 ===")
    
    # 測試告警模型
    alert = create_sample_alert()
    alert_dict = alert.model_dump()
    print(f"告警模型序列化: {json.dumps(alert_dict, indent=2, default=str, ensure_ascii=False)}")
    
    # 測試策略模型
    from models import QueryStrategy
    strategy = QueryStrategy(
        strategy_id="strategy_001",
        alert_id="alert_001",
        analysis="這是一個測試分析",
        queries=[
            {
                "query_id": "query_001",
                "description": "查詢錯誤日誌",
                "query": "level:ERROR",
                "purpose": "找出錯誤原因",
                "time_range": "last 1 hour",
                "expected_results": "錯誤日誌條目"
            }
        ],
        priority=1,
        estimated_time=30,
        success_probability=0.8
    )
    
    strategy_dict = strategy.model_dump()
    print(f"策略模型序列化: {json.dumps(strategy_dict, indent=2, default=str, ensure_ascii=False)}")

async def main():
    """主測試函數"""
    print("開始測試 Graylog Query Planner Service")
    print("=" * 50)
    
    # 測試數據模型
    test_models()
    
    # 測試AI分析器
    strategy = await test_ai_analyzer()
    
    # 測試查詢計劃器
    plan = await test_query_planner()
    
    # 測試A2A通信
    await test_a2a_communication()
    
    print("\n" + "=" * 50)
    print("測試完成")

if __name__ == "__main__":
    asyncio.run(main()) 