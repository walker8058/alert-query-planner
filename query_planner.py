import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from models import GraylogAlert, QueryStrategy, QueryPlan
from ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class QueryStep:
    """查詢步驟"""
    step_id: str
    query_id: str
    description: str
    query: str
    purpose: str
    time_range: str
    dependencies: List[str]
    priority: int
    estimated_time: int

class QueryPlanner:
    """查詢計劃器，負責生成和管理查詢計劃"""
    
    def __init__(self):
        """初始化查詢計劃器"""
        self.ai_analyzer = AIAnalyzer()
        self.plans: Dict[str, QueryPlan] = {}
    
    def create_query_plan(self, alert: GraylogAlert, strategy: QueryStrategy) -> QueryPlan:
        """創建查詢計劃"""
        try:
            # 生成計劃ID
            plan_id = str(uuid.uuid4())
            
            # 解析查詢策略
            query_steps = self._parse_strategy_to_steps(strategy)
            
            # 確定執行順序
            execution_order = self._determine_execution_order(query_steps)
            
            # 建立依賴關係
            dependencies = self._build_dependencies(query_steps)
            
            # 創建查詢計劃
            plan = QueryPlan(
                plan_id=plan_id,
                alert=alert,
                strategy=strategy,
                execution_order=execution_order,
                dependencies=dependencies,
                status="pending"
            )
            
            # 儲存計劃
            self.plans[plan_id] = plan
            
            logger.info(f"成功創建查詢計劃: {plan_id}")
            return plan
            
        except Exception as e:
            logger.error(f"創建查詢計劃失敗: {e}")
            raise
    
    def _parse_strategy_to_steps(self, strategy: QueryStrategy) -> List[QueryStep]:
        """將查詢策略解析為查詢步驟"""
        steps = []
        
        for i, query_data in enumerate(strategy.queries):
            step = QueryStep(
                step_id=str(uuid.uuid4()),
                query_id=query_data.get("query_id", f"query_{i}"),
                description=query_data.get("description", ""),
                query=query_data.get("query", ""),
                purpose=query_data.get("purpose", ""),
                time_range=query_data.get("time_range", "last 1 hour"),
                dependencies=query_data.get("dependencies", []),
                priority=query_data.get("priority", strategy.priority),
                estimated_time=query_data.get("estimated_time", 5)
            )
            steps.append(step)
        
        return steps
    
    def _determine_execution_order(self, steps: List[QueryStep]) -> List[str]:
        """確定查詢執行順序"""
        # 基於優先級和依賴關係排序
        sorted_steps = sorted(steps, key=lambda x: (x.priority, len(x.dependencies)))
        return [step.step_id for step in sorted_steps]
    
    def _build_dependencies(self, steps: List[QueryStep]) -> Dict[str, List[str]]:
        """建立依賴關係"""
        dependencies = {}
        
        for step in steps:
            dependencies[step.step_id] = step.dependencies
        
        return dependencies
    
    def get_plan(self, plan_id: str) -> Optional[QueryPlan]:
        """獲取查詢計劃"""
        return self.plans.get(plan_id)
    
    def update_plan_status(self, plan_id: str, status: str) -> bool:
        """更新計劃狀態"""
        try:
            if plan_id in self.plans:
                self.plans[plan_id].status = status
                self.plans[plan_id].updated_at = datetime.now()
                logger.info(f"更新計劃狀態: {plan_id} -> {status}")
                return True
            else:
                logger.warning(f"計劃不存在: {plan_id}")
                return False
        except Exception as e:
            logger.error(f"更新計劃狀態失敗: {e}")
            return False
    
    def get_plan_summary(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """獲取計劃摘要"""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return None
            
            return {
                "plan_id": plan.plan_id,
                "alert_id": plan.alert.alert_id,
                "status": plan.status,
                "total_queries": len(plan.strategy.queries),
                "estimated_total_time": plan.strategy.estimated_time,
                "success_probability": plan.strategy.success_probability,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"獲取計劃摘要失敗: {e}")
            return None
    
    def list_all_plans(self) -> List[Dict[str, Any]]:
        """列出所有計劃"""
        try:
            summaries = []
            for plan_id in self.plans:
                summary = self.get_plan_summary(plan_id)
                if summary:
                    summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"列出所有計劃失敗: {e}")
            return []
    
    def delete_plan(self, plan_id: str) -> bool:
        """刪除查詢計劃"""
        try:
            if plan_id in self.plans:
                del self.plans[plan_id]
                logger.info(f"刪除計劃: {plan_id}")
                return True
            else:
                logger.warning(f"計劃不存在: {plan_id}")
                return False
        except Exception as e:
            logger.error(f"刪除計劃失敗: {e}")
            return False
    
    def optimize_plan(self, plan_id: str) -> Optional[QueryPlan]:
        """優化查詢計劃"""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return None
            
            # 這裡可以實現更複雜的優化邏輯
            # 例如：合併相似查詢、調整執行順序等
            
            logger.info(f"優化計劃: {plan_id}")
            return plan
            
        except Exception as e:
            logger.error(f"優化計劃失敗: {e}")
            return None
    
    def validate_plan(self, plan_id: str) -> Dict[str, Any]:
        """驗證查詢計劃"""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return {"valid": False, "error": "計劃不存在"}
            
            validation_result = {
                "valid": True,
                "warnings": [],
                "errors": []
            }
            
            # 驗證告警信息
            if not plan.alert.alert_id:
                validation_result["errors"].append("告警ID缺失")
                validation_result["valid"] = False
            
            # 驗證查詢策略
            if not plan.strategy.queries:
                validation_result["errors"].append("查詢策略為空")
                validation_result["valid"] = False
            
            # 驗證執行順序
            if not plan.execution_order:
                validation_result["warnings"].append("執行順序為空")
            
            # 驗證依賴關係
            for step_id, deps in plan.dependencies.items():
                for dep in deps:
                    if dep not in plan.dependencies:
                        validation_result["warnings"].append(f"依賴關係無效: {step_id} -> {dep}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"驗證計劃失敗: {e}")
            return {"valid": False, "error": str(e)} 