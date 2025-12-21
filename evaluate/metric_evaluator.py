"""
评测指标处理器
实现6个评测指标的计算逻辑
"""
import json
import re
from typing import List, Tuple
from models_v2 import Memory, MetricResult, LLMConfig
from llm_service import LLMService
from prompt_service import PromptTemplateService
from metric_registry import register_metric


class MetricEvaluator:
    """评测指标处理器基类"""
    
    metric_name: str = ""  # 由装饰器设置
    
    def __init__(self, prompt_service: PromptTemplateService = None, llm_service: LLMService = None, llm_config: LLMConfig = None):
        self.prompt_service = prompt_service
        self.llm_service = llm_service
        self.llm_config = llm_config
    
    def _call_llm(self, prompt: str) -> dict:
        """调用LLM并解析JSON响应"""
        response = self.llm_service.chat(prompt, self.llm_config)
        
        # 尝试提取JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {}


@register_metric("accuracy")
class AccuracyEvaluator(MetricEvaluator):
    """
    精准度评测器（记忆提取场景）
    精准度 = 实际提取的记忆中命中测试集的记忆数 / 实际提取的记忆总数
    """
    
    def evaluate(self, expected_memories: List[Memory], actual_memories: List[Memory]) -> MetricResult:
        """
        评测精准度
        
        Args:
            expected_memories: 预期记忆列表
            actual_memories: 实际提取的记忆列表
            
        Returns:
            评测结果
        """
        if not actual_memories:
            return MetricResult(
                metric_name="accuracy",
                metric_value=1.0 if not expected_memories else 0.0,
                passed=True if not expected_memories else False,
                reason="实际未提取任何记忆"
            )
        
        # 调用LLM判断每个实际记忆是否命中预期记忆
        expected_contents = [m.content for m in expected_memories]
        actual_contents = [m.content for m in actual_memories]
        
        prompt = self.prompt_service.get_prompt(
            "memory_coverage",
            {
                "expected_memories": "\n".join(expected_contents),
                "actual_memories": "\n".join(actual_contents)
            }
        )
        
        llm_response = self._call_llm(prompt)
        
        # 解析匹配结果
        matching_map = llm_response.get("memory_matching_map", {})
        matching_details = llm_response.get("matching_details", [])
        
        hit_count = 0
        for actual_idx, expected_idx in matching_map.items():
            # 处理各种返回格式
            if isinstance(expected_idx, (int, str)):
                if expected_idx != -1 and expected_idx != "-1":
                    hit_count += 1
        
        accuracy = hit_count / len(actual_memories) if actual_memories else 0.0
        
        # 构建详细的reason
        reason_parts = [f"精准度: {accuracy:.1%} ({hit_count}/{len(actual_memories)})。"]
        
        if matching_details:
            reason_parts.append("\n\n匹配详情：")
            for detail in matching_details:
                actual_idx = detail.get("actual_index")
                actual_content = detail.get("actual_content", "")
                expected_idx = detail.get("expected_index")
                expected_content = detail.get("expected_content")
                match_reason = detail.get("match_reason", "")
                match_status = detail.get("match_status", "")
                
                if match_status == 'matched':
                    actual_text = (actual_content or "")[:50]
                    expected_text = (expected_content or "")[:50]
                    reason_parts.append(
                        f"\n✅ 实际记忆[{actual_idx}]: \"{actual_text}...\" "
                        f"\n   匹配到 预期记忆[{expected_idx}]: \"{expected_text}...\" "
                        f"\n   原因: {match_reason}"
                    )
                else:
                    actual_text = (actual_content or "")[:50]
                    reason_parts.append(
                        f"\n❌ 实际记忆[{actual_idx}]: \"{actual_text}...\" "
                        f"\n   未匹配到任何预期记忆"
                        f"\n   原因: {match_reason}"
                    )
        
        return MetricResult(
            metric_name="accuracy",
            metric_value=accuracy,
            passed=accuracy >= 0.6,
            reason="".join(reason_parts)
        )


@register_metric("completeness")
class CompletenessEvaluator(MetricEvaluator):
    """
    完整度评测器（记忆提取场景）
    完整度 = 命中测试集记忆数 / 测试集记忆总数
    """
    
    def evaluate(self, expected_memories: List[Memory], actual_memories: List[Memory]) -> MetricResult:
        """
        评测完整度
        
        Args:
            expected_memories: 预期记忆列表
            actual_memories: 实际提取的记忆列表
            
        Returns:
            评测结果
        """
        if not expected_memories:
            return MetricResult(
                metric_name="completeness",
                metric_value=1.0,
                passed=True,
                reason="无预期记忆"
            )
        
        if not actual_memories:
            return MetricResult(
                metric_name="completeness",
                metric_value=0.0,
                passed=False,
                reason="实际未提取任何记忆"
            )
        
        # 调用LLM判断预期记忆是否被实际记忆覆盖
        expected_contents = [m.content for m in expected_memories]
        actual_contents = [m.content for m in actual_memories]
        
        prompt = self.prompt_service.get_prompt(
            "memory_coverage",
            {
                "expected_memories": "\n".join(expected_contents),
                "actual_memories": "\n".join(actual_contents)
            }
        )
        
        llm_response = self._call_llm(prompt)
        
        # 解析匹配结果（反向统计）
        matching_map = llm_response.get("memory_matching_map", {})
        matching_details = llm_response.get("matching_details", [])
        
        covered_expected = set()
        for actual_idx, expected_idx in matching_map.items():
            # 处理各种返回格式
            if isinstance(expected_idx, (int, str)):
                if expected_idx != -1 and expected_idx != "-1":
                    covered_expected.add(str(expected_idx))
        
        hit_count = len(covered_expected)
        completeness = hit_count / len(expected_memories) if expected_memories else 0.0
        
        # 构建详细的reason
        reason_parts = [f"完整度: {completeness:.1%} ({hit_count}/{len(expected_memories)})。"]
        
        # 统计哪些预期记忆被匹配了
        expected_matched = {}
        for detail in matching_details:
            expected_idx = detail.get("expected_index")
            if expected_idx != -1:
                if expected_idx not in expected_matched:
                    expected_matched[expected_idx] = []
                expected_matched[expected_idx].append(detail)
        
        if expected_memories:
            reason_parts.append("\n\n预期记忆覆盖情况：")
            for i, expected_mem in enumerate(expected_memories):
                if i in expected_matched:
                    matched_detail = expected_matched[i][0]
                    actual_content = matched_detail.get("actual_content", "")
                    reason_parts.append(
                        f"\n✅ 预期记忆[{i}]: \"{expected_mem.content[:50]}...\" "
                        f"\n   被实际记忆匹配: \"{actual_content[:50]}...\""
                    )
                else:
                    reason_parts.append(
                        f"\n❌ 预期记忆[{i}]: \"{expected_mem.content[:50]}...\" "
                        f"\n   未被任何实际记忆匹配（缺失）"
                    )
        
        return MetricResult(
            metric_name="completeness",
            metric_value=completeness,
            passed=completeness >= 0.6,
            reason="".join(reason_parts)
        )


@register_metric("memory_duplication_effect")
class MemoryDuplicationEvaluator(MetricEvaluator):
    """
    记忆重复效果评测器（对话写入+召回场景）
    每组用例存在重复记忆记0，否则1
    """
    
    def evaluate(self, memories: List[Memory]) -> MetricResult:
        """
        评测记忆重复效果
        
        Args:
            memories: 召回的记忆列表
            
        Returns:
            评测结果
        """
        # 如果没有召回任何记忆，应该不通过
        if len(memories) == 0:
            return MetricResult(
                metric_name="memory_duplication_effect",
                metric_value=0.0,
                passed=False,
                reason="❌ 没有召回任何记忆"
            )
        
        # 如果只有1条记忆，无法判断重复，通过
        if len(memories) == 1:
            return MetricResult(
                metric_name="memory_duplication_effect",
                metric_value=1.0,
                passed=True,
                reason="✅ 只有1条记忆，无重复"
            )
        
        # 调用LLM判断是否存在重复
        memory_contents = [m.content for m in memories]
        
        prompt = self.prompt_service.get_prompt(
            "memory_duplication_detection",
            {
                "memories": "\n".join([f"{i+1}. {c}" for i, c in enumerate(memory_contents)])
            }
        )
        
        llm_response = self._call_llm(prompt)
        
        has_duplication = llm_response.get("has_duplication", False)
        score = 0.0 if has_duplication else 1.0
        
        duplication_pairs = llm_response.get("duplication_pairs", [])
        duplication_details = llm_response.get("duplication_details", [])
        analysis = llm_response.get("analysis", "")
        
        # 构建详细的reason
        if has_duplication:
            reason_parts = [f"⚠️ 存在重复记忆，评分: {score}\n"]
            if duplication_details:
                reason_parts.append("\n重复详情：")
                for detail in duplication_details:
                    pair = detail.get("pair", [])
                    mem1 = detail.get("memory1_content", "")
                    mem2 = detail.get("memory2_content", "")
                    reason = detail.get("reason", "")
                    reason_parts.append(
                        f"\n\n🔁 重复对 [{pair[0]}, {pair[1]}]:"
                        f"\n  记忆{pair[0]}: \"{mem1[:60]}...\""
                        f"\n  记忆{pair[1]}: \"{mem2[:60]}...\""
                        f"\n  原因: {reason}"
                    )
            if analysis:
                reason_parts.append(f"\n\n分析: {analysis}")
            return MetricResult(
                metric_name="memory_duplication_effect",
                metric_value=score,
                passed=score == 1.0,
                reason="".join(reason_parts)
            )
        else:
            return MetricResult(
                metric_name="memory_duplication_effect",
                metric_value=score,
                passed=score == 1.0,
                reason=f"✅ 不存在重复记忆。{analysis if analysis else ''}"
            )


@register_metric("memory_conflict_effect")
class MemoryConflictEvaluator(MetricEvaluator):
    """
    记忆冲突效果评测器（对话写入+召回场景）
    每组用例存在冲突记忆记0，否则1
    """
    
    def evaluate(self, memories: List[Memory]) -> MetricResult:
        """
        评测记忆冲突效果
        
        Args:
            memories: 召回的记忆列表
            
        Returns:
            评测结果
        """
        # 如果没有召回任何记忆，应该不通过
        if len(memories) == 0:
            return MetricResult(
                metric_name="memory_conflict_effect",
                metric_value=0.0,
                passed=False,
                reason="❌ 没有召回任何记忆"
            )
        
        # 如果只有1条记忆，无法判断冲突，通过
        if len(memories) == 1:
            return MetricResult(
                metric_name="memory_conflict_effect",
                metric_value=1.0,
                passed=True,
                reason="✅ 只有1条记忆，无冲突"
            )
        
        # 调用LLM判断是否存在冲突
        memory_contents = [m.content for m in memories]
        
        prompt = self.prompt_service.get_prompt(
            "memory_conflict_detection",
            {
                "memories": "\n".join([f"{i+1}. {c}" for i, c in enumerate(memory_contents)])
            }
        )
        
        llm_response = self._call_llm(prompt)
        
        has_conflict = llm_response.get("has_conflict", False)
        score = 0.0 if has_conflict else 1.0
        
        conflict_pairs = llm_response.get("conflict_pairs", [])
        conflict_details = llm_response.get("conflict_details", [])
        analysis = llm_response.get("analysis", "")
        
        # 构建详细的reason
        if has_conflict:
            reason_parts = [f"⚠️ 存在冲突记忆，评分: {score}\n"]
            if conflict_details:
                reason_parts.append("\n冲突详情：")
                for detail in conflict_details:
                    pair = detail.get("pair", [])
                    mem1 = detail.get("memory1_content", "")
                    mem2 = detail.get("memory2_content", "")
                    reason = detail.get("reason", "")
                    reason_parts.append(
                        f"\n\n⚡ 冲突对 [{pair[0]}, {pair[1]}]:"
                        f"\n  记忆{pair[0]}: \"{mem1[:60]}...\""
                        f"\n  记忆{pair[1]}: \"{mem2[:60]}...\""
                        f"\n  原因: {reason}"
                    )
            if analysis:
                reason_parts.append(f"\n\n分析: {analysis}")
            return MetricResult(
                metric_name="memory_conflict_effect",
                metric_value=score,
                passed=score == 1.0,
                reason="".join(reason_parts)
            )
        else:
            return MetricResult(
                metric_name="memory_conflict_effect",
                metric_value=score,
                passed=score == 1.0,
                reason=f"✅ 不存在冲突记忆。{analysis if analysis else ''}"
            )


@register_metric("recall_accuracy")
class RecallAccuracyEvaluator(MetricEvaluator):
    """
    召回精准度评测器（记忆写入+召回场景）
    精准度 = 实际召回的记忆中命中测试集的记忆数 / 实际召回的记忆总数
    通过记忆ID匹配，不需要调用LLM
    """
    
    def evaluate(self, expected_memories: List[Memory], actual_memories: List[Memory]) -> MetricResult:
        """
        评测召回精准度
        
        Args:
            expected_memories: 预期召回的记忆列表
            actual_memories: 实际召回的记忆列表
            
        Returns:
            评测结果
        """
        if not actual_memories:
            return MetricResult(
                metric_name="recall_accuracy",
                metric_value=1.0 if not expected_memories else 0.0,
                passed=True if not expected_memories else False,
                reason="实际未召回任何记忆"
            )
        
        # 计算命中数（通过ID匹配）
        expected_ids = {m.memory_id: m for m in expected_memories}
        actual_ids = {m.memory_id: m for m in actual_memories}
        
        hit_count = sum(1 for mid in actual_ids if mid in expected_ids)
        accuracy = hit_count / len(actual_memories) if actual_memories else 0.0
        
        # 构建详细的reason
        reason_parts = [f"精准度: {accuracy:.1%} ({hit_count}/{len(actual_memories)})。"]
        reason_parts.append("\n\n召回记忆匹配情况：")
        
        for mem in actual_memories:
            if mem.memory_id in expected_ids:
                expected_mem = expected_ids[mem.memory_id]
                reason_parts.append(
                    f"\n✅ 召回记忆[{mem.memory_id}]: \"{mem.content[:50]}...\" "
                    f"\n   匹配到预期记忆: \"{expected_mem.content[:50]}...\""
                )
            else:
                reason_parts.append(
                    f"\n❌ 召回记忆[{mem.memory_id}]: \"{mem.content[:50]}...\" "
                    f"\n   不在预期召回列表中（多余）"
                )
        
        return MetricResult(
            metric_name="recall_accuracy",
            metric_value=accuracy,
            passed=accuracy >= 0.6,
            reason="".join(reason_parts)
        )


@register_metric("recall_completeness")
class RecallCompletenessEvaluator(MetricEvaluator):
    """
    召回完整度评测器（记忆写入+召回场景）
    完整度 = 命中测试集记忆数 / 测试集记忆总数
    通过记忆ID匹配，不需要调用LLM
    """
    
    def evaluate(self, expected_memories: List[Memory], actual_memories: List[Memory]) -> MetricResult:
        """
        评测召回完整度
        
        Args:
            expected_memories: 预期召回的记忆列表
            actual_memories: 实际召回的记忆列表
            
        Returns:
            评测结果
        """
        if not expected_memories:
            return MetricResult(
                metric_name="recall_completeness",
                metric_value=1.0,
                passed=True,
                reason="无预期召回记忆"
            )
        
        if not actual_memories:
            return MetricResult(
                metric_name="recall_completeness",
                metric_value=0.0,
                passed=False,
                reason="实际未召回任何记忆"
            )
        
        # 计算命中数（通过ID匹配）
        expected_ids = {m.memory_id: m for m in expected_memories}
        actual_ids = {m.memory_id: m for m in actual_memories}
        
        hit_count = sum(1 for mid in expected_ids if mid in actual_ids)
        completeness = hit_count / len(expected_memories) if expected_memories else 0.0
        
        # 构建详细的reason
        reason_parts = [f"完整度: {completeness:.1%} ({hit_count}/{len(expected_memories)})。"]
        reason_parts.append("\n\n预期召回记忆覆盖情况：")
        
        for mem in expected_memories:
            if mem.memory_id in actual_ids:
                actual_mem = actual_ids[mem.memory_id]
                reason_parts.append(
                    f"\n✅ 预期记忆[{mem.memory_id}]: \"{mem.content[:50]}...\" "
                    f"\n   已被召回: \"{actual_mem.content[:50]}...\""
                )
            else:
                reason_parts.append(
                    f"\n❌ 预期记忆[{mem.memory_id}]: \"{mem.content[:50]}...\" "
                    f"\n   未被召回（缺失）"
                )
        
        return MetricResult(
            metric_name="recall_completeness",
            metric_value=completeness,
            passed=completeness >= 0.6,
            reason="".join(reason_parts)
        )
