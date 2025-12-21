"""
批量评测脚本
支持从多个数据文件加载并批量执行评测
"""
import json
from pathlib import Path
from typing import List

from models_v2 import EvaluationDataItem, CaseResult
from case_loader import CaseLoader
from memory_system_interface import MockMemorySystem
from evaluation_engine import EvaluationEngine
from config_loader import ConfigLoader
from llm_service import LLMService
from prompt_service import PromptTemplateService
from scenario_factory import ScenarioFactory
from report_generator import ReportGenerator
from report_visualizer import ReportVisualizer


def load_data_items(file_path: str) -> List[EvaluationDataItem]:
    """
    从JSON文件加载评测数据项
    支持单个对象或数组格式
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return [EvaluationDataItem(**item) for item in data]
    else:
        return [EvaluationDataItem(**data)]


def evaluate_all_items(
    data_items: List[EvaluationDataItem],
    scenarios: List[str] = None,
    metrics: List[str] = None
):
    """
    批量评测所有数据项
    
    Args:
        data_items: 评测数据项列表
        scenarios: 要评测的场景列表，默认为所有场景
        metrics: 要评测的指标列表，默认使用场景的默认指标
    """
    # 智能推断场景
    if scenarios is None:
        if metrics is not None:
            # 如果指定了metrics但没指定scenarios，根据metrics推断应该评测哪些场景
            scenarios = ScenarioFactory.get_scenarios_for_metrics(metrics)
            if not scenarios:
                print(f"\n警告: 指定的指标 {metrics} 不属于任何已知场景，将使用所有场景")
                scenarios = ["dialogue_extraction", "memory_write_recall", "conversation_write_recall"]
        else:
            # 都没指定，使用所有场景
            scenarios = ["dialogue_extraction", "memory_write_recall", "conversation_write_recall"]
    
    # 初始化
    print("\n" + "=" * 100)
    print(" 批量评测系统 ".center(100, "="))
    print("=" * 100)
    
    print(f"\n数据项数量: {len(data_items)}")
    print(f"评测场景: {', '.join(scenarios)}")
    
    # 加载配置
    print("\n初始化评测环境...")
    config = ConfigLoader.load_default()
    llm_service = LLMService()
    prompt_service = PromptTemplateService(config.prompts)
    memory_system = MockMemorySystem()
    engine = EvaluationEngine(memory_system, prompt_service, llm_service, config.llm)
    
    # 收集所有结果
    all_results = []
    
    # 遍历每个数据项
    for idx, data_item in enumerate(data_items, 1):
        print("\n" + "=" * 100)
        print(f" 数据项 {idx}/{len(data_items)}: {data_item.item_name} ".center(100, "="))
        print("=" * 100)
        
        # 加载用例
        all_cases = CaseLoader.load_all_cases(data_item)
        
        # 使用工厂模式执行评测
        for scenario_idx, scenario_name in enumerate(scenarios, 1):
            # 从工厂获取场景配置
            config = ScenarioFactory.get_config(scenario_name)
            
            # 获取该场景的用例
            cases = all_cases.get(config.case_key, [])
            if not cases:
                continue
            
            # 确定该场景要评测的指标
            if metrics is not None:
                # 过滤出该场景支持的指标
                eval_metrics = ScenarioFactory.filter_metrics_for_scenario(scenario_name, metrics)
                if not eval_metrics:
                    # 如果该场景不支持任何用户指定的指标，跳过
                    print(f"\n[场景{scenario_idx}] {config.display_name} - 跳过（不支持指定的指标）")
                    continue
            else:
                # 使用场景默认指标
                eval_metrics = config.default_metrics
            
            # 打印场景信息
            print(f"\n[场景{scenario_idx}] {config.display_name} - {len(cases)} 个用例 - 指标: {', '.join(eval_metrics)}")
            
            # 统一的评测接口
            results = engine.evaluate(
                scenario_name=config.scenario_name,
                cases=cases,
                metrics=eval_metrics
            )
            all_results.extend(results)
    
    # 生成综合报告
    print("\n" + "=" * 100)
    print(" 生成综合报告 ".center(100, "="))
    print("=" * 100)
    
    # 使用ReportGenerator生成报告
    report = ReportGenerator.generate_report(
        all_results, 
        f"批量评测报告 ({len(data_items)}个数据项)"
    )
    
    # 打印报告
    print_report(report)
    
    # 保存报告
    save_report(report)


def print_report(report):
    """打印评测报告"""
    print("\n" + "=" * 100)
    print(f" 评测报告: {report.report_name} ".center(100, "="))
    print("=" * 100)
    
    print(f"\n报告ID: {report.report_id}")
    print(f"生成时间: {report.create_time}")
    print(f"总用例数: {report.summary['total_cases']}")
    
    # 按场景分组统计
    print("\n" + "-" * 100)
    print("场景统计")
    print("-" * 100)
    
    scenario_stats = {}
    for case_result in report.case_results:
        case_type = case_result.case_type
        if case_type not in scenario_stats:
            scenario_stats[case_type] = {"total": 0, "passed": 0}
        
        scenario_stats[case_type]["total"] += 1
        if all(m.passed for m in case_result.metrics):
            scenario_stats[case_type]["passed"] += 1
    
    for scenario, stats in scenario_stats.items():
        pass_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"{scenario}: {stats['passed']}/{stats['total']} 通过 ({pass_rate:.1f}%)")
    
    # 指标汇总
    print("\n" + "-" * 100)
    print("指标汇总")
    print("-" * 100)
    
    for metric_name, stats in report.summary["metrics"].items():
        print(f"\n{metric_name}:")
        print(f"  平均值: {stats['average']:.4f} ({stats['average']*100:.2f}%)")
        print(f"  通过数: {stats['passed_count']}/{stats['total_count']}")
        print(f"  通过率: {stats['pass_rate']*100:.2f}%")
    
    # 详细结果（可选）
    print("\n" + "-" * 100)
    print("详细结果")
    print("-" * 100)
    
    for case_result in report.case_results:
        print(f"\n[{case_result.case_type}] {case_result.case_id}")
        for metric in case_result.metrics:
            status = "✓" if metric.passed else "✗"
            print(f"  [{status}] {metric.metric_name}: {metric.metric_value:.4f}")
    
    print("\n" + "=" * 100)


def save_report(report):
    """保存评测报告到文件（JSON + HTML）"""
    output_dir = Path(__file__).parent.parent / "reports"
    output_dir.mkdir(exist_ok=True)
    
    # 保存JSON报告
    json_file = output_dir / f"{report.report_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"\n📄 JSON报告已保存到: {json_file}")
    
    # 生成并保存HTML报告
    html_file = output_dir / f"{report.report_id}.html"
    ReportVisualizer.generate_html(report, str(html_file))
    print(f"🌐 HTML报告已保存到: {html_file}")
    print(f"\n💡 在浏览器中打开HTML文件查看可视化报告")


if __name__ == "__main__":
    import sys
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='批量评测脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 使用默认数据和默认指标
  python3 batch_evaluation.py
  
  # 指定数据文件
  python3 batch_evaluation.py data.json
  
  # 指定评测指标
  python3 batch_evaluation.py --metrics accuracy completeness
  
  # 指定数据文件和评测指标
  python3 batch_evaluation.py data.json --metrics recall_accuracy recall_completeness
  
  # 指定场景和指标
  python3 batch_evaluation.py --scenarios dialogue_extraction --metrics accuracy
        ''')
    
    parser.add_argument(
        'data_file',
        nargs='?',
        default=None,
        help='评测数据文件路径（JSON格式）'
    )
    
    parser.add_argument(
        '--metrics',
        nargs='+',
        default=None,
        help='指定要评测的指标列表，可选值: accuracy, completeness, recall_accuracy, recall_completeness, memory_duplication_effect, memory_conflict_effect'
    )
    
    parser.add_argument(
        '--scenarios',
        nargs='+',
        default=None,
        help='指定要评测的场景列表，可选值: dialogue_extraction, memory_write_recall, conversation_write_recall'
    )
    
    args = parser.parse_args()
    
    # 确定数据文件
    if args.data_file:
        data_file = args.data_file
    else:
        default_file = Path(__file__).parent.parent / "data" / "test_data_complete_v2.json"
        data_file = str(default_file)
    
    print(f"\n加载测试数据: {data_file}")
    
    # 显示评测配置
    if args.metrics:
        print(f"指定评测指标: {', '.join(args.metrics)}")
    else:
        print("使用场景默认指标")
    
    if args.scenarios:
        print(f"指定评测场景: {', '.join(args.scenarios)}")
    else:
        print("评测所有场景")
    
    try:
        data_items = load_data_items(data_file)
        evaluate_all_items(data_items, scenarios=args.scenarios, metrics=args.metrics)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
