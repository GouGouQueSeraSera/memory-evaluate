"""
评测报告生成器
负责解析评测结果并生成报告
"""
import uuid
from typing import List, Dict
from models_v2 import CaseResult, EvaluationReport


class ReportGenerator:
    """评测报告生成器"""
    
    @staticmethod
    def generate_report(
        case_results: List[CaseResult],
        report_name: str
    ) -> EvaluationReport:
        """
        生成评测报告
        
        Args:
            case_results: 用例评测结果列表
            report_name: 报告名称
            
        Returns:
            评测报告
        """
        # 统计各指标的平均值
        metric_stats = {}
        
        for case_result in case_results:
            for metric in case_result.metrics:
                if metric.metric_name not in metric_stats:
                    metric_stats[metric.metric_name] = []
                metric_stats[metric.metric_name].append(metric.metric_value)
        
        # 计算平均值和通过率
        summary = {
            "total_cases": len(case_results),
            "metrics": {}
        }
        
        for metric_name, values in metric_stats.items():
            avg_value = sum(values) / len(values) if values else 0.0
            passed_count = sum(1 for v in values if v >= 0.6)
            summary["metrics"][metric_name] = {
                "average": avg_value,
                "passed_count": passed_count,
                "total_count": len(values),
                "pass_rate": passed_count / len(values) if values else 0.0
            }
        
        report = EvaluationReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            report_name=report_name,
            case_results=case_results,
            summary=summary
        )
        
        return report
    
    @staticmethod
    def get_scenario_statistics(case_results: List[CaseResult]) -> Dict[str, Dict]:
        """
        按场景统计评测结果
        
        Args:
            case_results: 用例评测结果列表
            
        Returns:
            场景统计信息字典
        """
        scenario_stats = {}
        
        for case_result in case_results:
            scenario = case_result.case_type
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {
                    "total": 0,
                    "passed": 0
                }
            
            scenario_stats[scenario]["total"] += 1
            
            # 判断用例是否通过（所有指标都通过）
            if all(metric.passed for metric in case_result.metrics):
                scenario_stats[scenario]["passed"] += 1
        
        # 计算通过率
        for scenario, stats in scenario_stats.items():
            stats["pass_rate"] = stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0
        
        return scenario_stats
    
    @staticmethod
    def get_metric_statistics(case_results: List[CaseResult]) -> Dict[str, Dict]:
        """
        按指标统计评测结果
        
        Args:
            case_results: 用例评测结果列表
            
        Returns:
            指标统计信息字典
        """
        metric_stats = {}
        
        for case_result in case_results:
            for metric in case_result.metrics:
                if metric.metric_name not in metric_stats:
                    metric_stats[metric.metric_name] = {
                        "values": [],
                        "passed_count": 0,
                        "total_count": 0
                    }
                
                metric_stats[metric.metric_name]["values"].append(metric.metric_value)
                metric_stats[metric.metric_name]["total_count"] += 1
                if metric.passed:
                    metric_stats[metric.metric_name]["passed_count"] += 1
        
        # 计算平均值和通过率
        for metric_name, stats in metric_stats.items():
            values = stats["values"]
            stats["average"] = sum(values) / len(values) if values else 0.0
            stats["pass_rate"] = stats["passed_count"] / stats["total_count"] if stats["total_count"] > 0 else 0.0
            # 移除临时的values列表
            del stats["values"]
        
        return metric_stats
