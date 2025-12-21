"""
评测报告可视化生成器
生成美观的HTML报告
"""
from typing import Dict, Any, List
from models_v2 import EvaluationReport, CaseResult, MetricResult
from pathlib import Path


class ReportVisualizer:
    """报告可视化器"""
    
    @staticmethod
    def generate_html(report: EvaluationReport, output_path: str = None) -> str:
        """
        生成HTML报告
        
        Args:
            report: 评测报告对象
            output_path: 输出路径，如果为None则只返回HTML字符串
            
        Returns:
            HTML字符串
        """
        html = ReportVisualizer._build_html(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
    
    @staticmethod
    def _build_html(report: EvaluationReport) -> str:
        """构建HTML内容"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.report_name}</title>
    <style>
        {ReportVisualizer._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {ReportVisualizer._build_header(report)}
        {ReportVisualizer._build_summary(report)}
        {ReportVisualizer._build_cases(report)}
    </div>
    <script>
        {ReportVisualizer._get_javascript()}
    </script>
</body>
</html>"""
        return html
    
    @staticmethod
    def _get_css() -> str:
        """获取CSS样式"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .meta {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .summary {
            padding: 40px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .summary h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .metric-card h3 {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .metric-details {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .cases {
            padding: 40px;
        }
        
        .cases h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 0;
        }
        
        .tab-button {
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s;
        }
        
        .tab-button:hover {
            color: #667eea;
            background: #f8f9fa;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .case-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .case-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 2px solid #e9ecef;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .case-header:hover {
            background: #e9ecef;
        }
        
        .case-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #495057;
        }
        
        .case-type {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 15px;
        }
        
        .type-dialogue_extraction {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .type-memory_write_recall {
            background: #f3e5f5;
            color: #7b1fa2;
        }
        
        .type-conversation_write_recall {
            background: #e8f5e9;
            color: #388e3c;
        }
        
        .case-body {
            padding: 20px;
            display: none;
        }
        
        .case-body.active {
            display: block;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .metric-result {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .metric-result.passed {
            border-left-color: #28a745;
            background: #d4edda;
        }
        
        .metric-result.failed {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        
        .metric-name {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .metric-score {
            font-size: 1.5em;
            color: #667eea;
        }
        
        .metric-reason {
            color: #495057;
            line-height: 1.6;
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }
        
        .conversation {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        .message {
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            line-height: 1.6;
        }
        
        .message.user {
            background: #e3f2fd;
            border-left: 4px solid #1976d2;
        }
        
        .message.assistant {
            background: #f3e5f5;
            border-left: 4px solid #7b1fa2;
        }
        
        .message-role {
            font-weight: bold;
            margin-bottom: 5px;
            color: #495057;
        }
        
        .memory-list {
            list-style: none;
        }
        
        .memory-item {
            background: #f8f9fa;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        
        .memory-id {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .memory-content {
            color: #495057;
            line-height: 1.6;
        }
        
        .match-status {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .match-status.matched {
            background: #d4edda;
            color: #155724;
        }
        
        .match-status.missing {
            background: #fff3cd;
            color: #856404;
        }
        
        .match-status.extra {
            background: #f8d7da;
            color: #721c24;
        }
        
        .toggle-icon {
            font-size: 1.5em;
            transition: transform 0.3s;
        }
        
        .toggle-icon.active {
            transform: rotate(180deg);
        }
        
        .qa-section {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
        }
        
        .qa-label {
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 5px;
        }
        
        .qa-content {
            color: #495057;
            line-height: 1.6;
        }
        """
    
    @staticmethod
    def _get_javascript() -> str:
        """获取JavaScript代码"""
        return """
        function toggleCase(caseId) {
            const body = document.getElementById('case-body-' + caseId);
            const icon = document.getElementById('toggle-icon-' + caseId);
            
            body.classList.toggle('active');
            icon.classList.toggle('active');
        }
        
        function switchTab(scenarioName) {
            // 隐藏所有tab内容
            const allContents = document.querySelectorAll('.tab-content');
            allContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // 移除所有tab按钮的active状态
            const allButtons = document.querySelectorAll('.tab-button');
            allButtons.forEach(button => {
                button.classList.remove('active');
            });
            
            // 显示选中的tab内容
            const selectedContent = document.getElementById('tab-' + scenarioName);
            if (selectedContent) {
                selectedContent.classList.add('active');
            }
            
            // 激活选中的tab按钮
            const selectedButton = event.target;
            selectedButton.classList.add('active');
        }
        
        // 默认展开第一个case
        document.addEventListener('DOMContentLoaded', function() {
            const firstCase = document.querySelector('.case-card');
            if (firstCase) {
                const caseId = firstCase.dataset.caseId;
                toggleCase(caseId);
            }
        });
        """
    
    @staticmethod
    def _build_header(report: EvaluationReport) -> str:
        """构建报告头部"""
        return f"""
        <div class="header">
            <h1>📊 {report.report_name}</h1>
            <div class="meta">
                <p>报告ID: {report.report_id}</p>
                <p>生成时间: {report.create_time}</p>
                <p>总用例数: {report.summary.get('total_cases', 0)}</p>
            </div>
        </div>
        """
    
    @staticmethod
    def _build_summary(report: EvaluationReport) -> str:
        """构建汇总信息"""
        metrics_html = ""
        
        for metric_name, stats in report.summary.get('metrics', {}).items():
            avg_value = stats.get('average', 0)
            pass_rate = stats.get('pass_rate', 0)
            passed = stats.get('passed_count', 0)
            total = stats.get('total_count', 0)
            
            metrics_html += f"""
            <div class="metric-card">
                <h3>{metric_name}</h3>
                <div class="metric-value">{avg_value:.2%}</div>
                <div class="metric-details">
                    通过率: {pass_rate:.1%}<br>
                    通过数: {passed}/{total}
                </div>
            </div>
            """
        
        return f"""
        <div class="summary">
            <h2>📈 评测汇总</h2>
            <div class="metrics-grid">
                {metrics_html}
            </div>
        </div>
        """
    
    @staticmethod
    def _build_cases(report: EvaluationReport) -> str:
        """构建用例详情（按场景分Tab页）"""
        # 按场景分组
        scenarios = {}
        for idx, case_result in enumerate(report.case_results):
            scenario = case_result.case_type
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append((idx, case_result))
        
        # 如果只有一个场景，不使用Tab
        if len(scenarios) == 1:
            cases_html = ""
            for idx, case_result in enumerate(report.case_results):
                cases_html += ReportVisualizer._build_case_card(case_result, idx)
            
            return f"""
            <div class="cases">
                <h2>📝 用例详情</h2>
                {cases_html}
            </div>
            """
        
        # 多个场景，使用Tab页
        # 构建Tab标签
        tabs_html = ""
        scenario_names = {
            "dialogue_extraction": "记忆提取",
            "memory_write_recall": "记忆写入+召回",
            "conversation_write_recall": "对话写入+召回"
        }
        
        for scenario_idx, scenario in enumerate(scenarios.keys()):
            active_class = "active" if scenario_idx == 0 else ""
            display_name = scenario_names.get(scenario, scenario)
            count = len(scenarios[scenario])
            tabs_html += f"""
            <button class="tab-button {active_class}" onclick="switchTab('{scenario}')">{display_name} ({count})</button>
            """
        
        # 构建Tab内容
        tab_contents_html = ""
        for scenario_idx, (scenario, cases) in enumerate(scenarios.items()):
            active_class = "active" if scenario_idx == 0 else ""
            cases_html = ""
            for idx, case_result in cases:
                cases_html += ReportVisualizer._build_case_card(case_result, idx)
            
            tab_contents_html += f"""
            <div id="tab-{scenario}" class="tab-content {active_class}">
                {cases_html}
            </div>
            """
        
        return f"""
        <div class="cases">
            <h2>📝 用例详情</h2>
            <div class="tabs">
                {tabs_html}
            </div>
            {tab_contents_html}
        </div>
        """
    
    @staticmethod
    def _build_case_card(case: CaseResult, idx: int) -> str:
        """构建单个用例卡片"""
        case_id = f"case-{idx}"
        
        # 构建指标结果
        metrics_html = ""
        for metric in case.metrics:
            status_class = "passed" if metric.passed else "failed"
            status_icon = "✓" if metric.passed else "✗"
            
            metrics_html += f"""
            <div class="metric-result {status_class}">
                <div class="metric-name">
                    <span>{status_icon} {metric.metric_name}</span>
                    <span class="metric-score">{metric.metric_value:.2%}</span>
                </div>
                <div class="metric-reason">{metric.reason}</div>
            </div>
            """
        
        # 构建场景特定详情
        scenario_html = ReportVisualizer._build_scenario_details(
            case.case_type,
            case.scenario_details or {}
        )
        
        return f"""
        <div class="case-card" data-case-id="{case_id}">
            <div class="case-header" onclick="toggleCase('{case_id}')">
                <div>
                    <span class="case-title">{case.case_id}</span>
                    <span class="case-type type-{case.case_type}">{case.case_type}</span>
                </div>
                <span class="toggle-icon" id="toggle-icon-{case_id}">▼</span>
            </div>
            <div class="case-body" id="case-body-{case_id}">
                <div class="section">
                    <h3>📊 评测指标</h3>
                    {metrics_html}
                </div>
                {scenario_html}
            </div>
        </div>
        """
    
    @staticmethod
    def _build_scenario_details(case_type: str, details: Dict[str, Any]) -> str:
        """构建场景特定详情"""
        if case_type == "dialogue_extraction":
            return ReportVisualizer._build_dialogue_extraction_details(details)
        elif case_type == "memory_write_recall":
            return ReportVisualizer._build_memory_write_recall_details(details)
        elif case_type == "conversation_write_recall":
            return ReportVisualizer._build_conversation_write_recall_details(details)
        return ""
    
    @staticmethod
    def _build_dialogue_extraction_details(details: Dict[str, Any]) -> str:
        """构建记忆提取场景详情"""
        # 对话记录
        conversation_html = ""
        for msg in details.get('conversation', []):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation_html += f"""
            <div class="message {role}">
                <div class="message-role">{role.upper()}</div>
                <div>{content}</div>
            </div>
            """
        
        # 预期记忆
        expected_html = ""
        for mem in details.get('expected_memories', []):
            expected_html += f"""
            <li class="memory-item">
                <div class="memory-id">ID: {mem.get('memory_id', '')}</div>
                <div class="memory-content">{mem.get('content', '')}</div>
            </li>
            """
        
        # 实际记忆
        actual_html = ""
        for mem in details.get('actual_memories', []):
            actual_html += f"""
            <li class="memory-item">
                <div class="memory-id">ID: {mem.get('memory_id', '')}</div>
                <div class="memory-content">{mem.get('content', '')}</div>
            </li>
            """
        
        return f"""
        <div class="section">
            <h3>💬 原始对话</h3>
            <div class="conversation">
                {conversation_html}
            </div>
        </div>
        <div class="section">
            <h3>🎯 预期记忆</h3>
            <ul class="memory-list">
                {expected_html}
            </ul>
        </div>
        <div class="section">
            <h3>📝 实际提取的记忆</h3>
            <ul class="memory-list">
                {actual_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def _build_memory_write_recall_details(details: Dict[str, Any]) -> str:
        """构建记忆写入+召回场景详情"""
        # QA部分（只显示问题）
        qa_html = f"""
        <div class="qa-section">
            <div class="qa-label">问题 (Question):</div>
            <div class="qa-content">{details.get('question', '')}</div>
        </div>
        """
        
        # 写入的记忆
        written_html = ""
        for mem in details.get('written_memories', []):
            written_html += f"""
            <li class="memory-item">
                <div class="memory-id">ID: {mem.get('memory_id', '')}</div>
                <div class="memory-content">{mem.get('content', '')}</div>
            </li>
            """
        
        # 预期召回的记忆（根据expected_memory_ids从写入的记忆中筛选）
        expected_memory_ids = details.get('expected_memory_ids', [])
        written_memories = details.get('written_memories', [])
        expected_recalled_html = ""
        for mem in written_memories:
            if mem.get('memory_id') in expected_memory_ids:
                expected_recalled_html += f"""
                <li class="memory-item">
                    <div class="memory-id">ID: {mem.get('memory_id', '')}</div>
                    <div class="memory-content">{mem.get('content', '')}</div>
                </li>
                """
        
        # 实际召回的记忆
        recalled_html = ""
        for mem in details.get('actual_recalled_memories', []):
            recalled_html += f"""
            <li class="memory-item">
                <div class="memory-id">ID: {mem.get('memory_id', '')}</div>
                <div class="memory-content">{mem.get('content', '')}</div>
            </li>
            """
        
        return f"""
        <div class="section">
            <h3>❓ 问题</h3>
            {qa_html}
        </div>
        <div class="section">
            <h3>💾 写入的记忆</h3>
            <ul class="memory-list">
                {written_html}
            </ul>
        </div>
        <div class="section">
            <h3>🎯 预期召回的记忆</h3>
            <ul class="memory-list">
                {expected_recalled_html}
            </ul>
        </div>
        <div class="section">
            <h3>🔄 实际召回的记忆</h3>
            <ul class="memory-list">
                {recalled_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def _build_conversation_write_recall_details(details: Dict[str, Any]) -> str:
        """构建对话写入+召回场景详情"""
        # QA部分
        qa_html = f"""
        <div class="qa-section">
            <div class="qa-label">问题 (Question):</div>
            <div class="qa-content">{details.get('question', '')}</div>
        </div>
        <div class="qa-section">
            <div class="qa-label">答案 (Answer):</div>
            <div class="qa-content">{details.get('answer', '')}</div>
        </div>
        """
        
        # 对话记录
        conversation_html = ""
        for msg in details.get('conversation', []):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation_html += f"""
            <div class="message {role}">
                <div class="message-role">{role.upper()}</div>
                <div>{content}</div>
            </div>
            """
        
        # 实际召回的记忆
        recalled_html = ""
        for mem in details.get('actual_recalled_memories', []):
            recalled_html += f"""
            <li class="memory-item">
                <div class="memory-id">ID: {mem.get('memory_id', '')}</div>
                <div class="memory-content">{mem.get('content', '')}</div>
            </li>
            """
        
        return f"""
        <div class="section">
            <h3>❓ 问答信息</h3>
            {qa_html}
        </div>
        <div class="section">
            <h3>💬 原始对话</h3>
            <div class="conversation">
                {conversation_html}
            </div>
        </div>
        <div class="section">
            <h3>🔄 实际召回的记忆</h3>
            <ul class="memory-list">
                {recalled_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def _build_memory_matches(matches: List[Dict[str, Any]]) -> str:
        """构建记忆匹配详情"""
        if not matches:
            return "<p>无匹配信息</p>"
        
        matches_html = ""
        for match in matches:
            status = match.get('match_status', 'unknown')
            status_text = {
                'matched': '✓ 匹配',
                'missing': '⚠ 缺失',
                'extra': '➕ 额外'
            }.get(status, status)
            
            expected_id = match.get('expected_memory_id', '')
            expected_content = match.get('expected_content', '')
            actual_id = match.get('actual_memory_id', '')
            actual_content = match.get('actual_content', '')
            
            if status == 'matched':
                matches_html += f"""
                <div class="memory-item">
                    <div class="memory-id">
                        ID: {expected_id}
                        <span class="match-status {status}">{status_text}</span>
                    </div>
                    <div class="memory-content">{expected_content}</div>
                </div>
                """
            elif status == 'missing':
                matches_html += f"""
                <div class="memory-item">
                    <div class="memory-id">
                        预期ID: {expected_id}
                        <span class="match-status {status}">{status_text}</span>
                    </div>
                    <div class="memory-content">{expected_content}</div>
                </div>
                """
            elif status == 'extra':
                matches_html += f"""
                <div class="memory-item">
                    <div class="memory-id">
                        实际ID: {actual_id}
                        <span class="match-status {status}">{status_text}</span>
                    </div>
                    <div class="memory-content">{actual_content}</div>
                </div>
                """
        
        return f'<ul class="memory-list">{matches_html}</ul>'
