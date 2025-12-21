# 记忆系统评测框架

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个专为聊天机器人（虚拟人）记忆系统设计的全流程评测框架，支持从记忆提取、写入到召回的完整评测链路。

## 📋 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [评测场景](#评测场景)
- [评测指标](#评测指标)
- [数据格式](#数据格式)
- [使用指南](#使用指南)
- [扩展开发](#扩展开发)
- [常见问题](#常见问题)

## 项目简介

随着人工智能技术的快速发展，聊天机器人已经广泛应用于客户服务、智能助手、虚拟陪伴等多个领域。用户期望机器人能够记住他们的习惯、偏好和情感状态，提供更加个性化和连贯的交互体验。

本项目提供了一套完整的记忆系统评测框架，解决了现有技术方案的以下问题：

- ❌ **现有方案局限**：仅关注记忆提取环节，无法全面评估记忆系统
- ❌ **数据结构混乱**：缺乏统一的评测数据结构，难以复用
- ❌ **指标单一**：无法全面反映记忆系统的表现
- ❌ **扩展性差**：难以适应新的评测需求

✅ **本框架优势**：

- ✅ **全流程评测**：覆盖记忆提取、写入、召回全链路
- ✅ **统一数据结构**：一份数据支持多种评测场景
- ✅ **多维度指标**：从精准度、完整度、重复性、冲突性等多角度评估
- ✅ **高度可扩展**：支持自定义场景和指标
- ✅ **自动化评测**：结合大模型实现智能评测判断

## 核心特性

### 🎯 三大评测场景

1. **记忆提取评测（dialogue_extraction）**
   - 评估从对话中提取记忆的能力
   - 支持指标：accuracy（精准度）、completeness（完整度）

2. **记忆写入+召回（memory_write_recall）**
   - 评估记忆写入和召回的准确性
   - 支持指标：recall_accuracy（召回精准度）、recall_completeness（召回完整度）

3. **对话写入+召回（conversation_write_recall）**
   - 评估从对话到记忆提取、写入再到召回的全流程效果
   - 支持指标：memory_duplication_effect（记忆去重效果）、memory_conflict_effect（记忆冲突处理效果）

### 📊 六大评测指标

| 指标 | 场景 | 说明 | 需要LLM |
|------|------|------|---------|
| accuracy | 记忆提取 | 实际提取的记忆中命中预期的比例 | ✅ |
| completeness | 记忆提取 | 预期记忆被实际提取覆盖的比例 | ✅ |
| recall_accuracy | 记忆召回 | 实际召回的记忆中命中预期的比例 | ❌ |
| recall_completeness | 记忆召回 | 预期记忆被实际召回覆盖的比例 | ❌ |
| memory_duplication_effect | 全流程 | 是否存在重复记忆（0/1） | ✅ |
| memory_conflict_effect | 全流程 | 是否存在冲突记忆（0/1） | ✅ |

### 🏗️ 设计模式

- **策略模式**：不同评测场景使用不同的评测策略
- **工厂模式**：场景和指标的动态创建和管理
- **模板方法模式**：统一的评测流程模板
- **注册表模式**：指标的注册和查找机制

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      评测数据项                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  sessions   │  │     qa      │  │  evidence   │         │
│  │ (原始对话)   │  │  (问答对)    │  │  (关联关系)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    场景工厂（ScenarioFactory）                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 记忆提取场景  │  │ 写入召回场景  │  │ 全流程场景    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   评测引擎（EvaluationEngine）                │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │              指标注册表（MetricRegistry）            │     │
│  │  accuracy │ completeness │ recall_accuracy │ ...   │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   报告生成器（ReportGenerator）               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  JSON报告     │  │  HTML报告     │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求

- Python 3.8+
- 依赖包：见 `requirements.txt`

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd memory-evaluate

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 配置 LLM 服务（用于智能评测判断）

编辑 `data/config.yaml`：

```yaml
llm:
  api_url: "your_llm_api_url"
  api_key: "your_api_key"
  model: "your_model_name"
```

2. 准备评测数据

参考 `data/test_data_complete_v2.json` 格式准备评测数据。

### 运行评测

```bash
cd evaluate

# 使用默认配置运行所有评测
python3 batch_evaluation.py

# 指定评测指标（自动推断场景）
python3 batch_evaluation.py --metrics accuracy completeness

# 指定评测场景和指标
python3 batch_evaluation.py --scenarios dialogue_extraction --metrics accuracy

# 使用自定义数据文件
python3 batch_evaluation.py ../data/your_test_data.json --metrics accuracy
```

### 查看报告

评测完成后，报告将保存在 `reports/` 目录：

- `report_xxx.json`：JSON 格式的详细报告
- `report_xxx.html`：可视化 HTML 报告（在浏览器中打开查看）

## 评测场景

### 1. 记忆提取评测（dialogue_extraction）

**目的**：评估从对话中提取记忆的能力

**评测流程**：
```
原始对话 → 记忆提取模块 → 提取的记忆 → 与预期记忆比较 → 计算指标
```

**使用的数据**：
- `sessions[].conversation`：原始对话
- `sessions[].memories`：预期提取的记忆

**支持的指标**：
- `accuracy`：精准度
- `completeness`：完整度

**示例**：
```bash
python3 batch_evaluation.py --scenarios dialogue_extraction --metrics accuracy completeness
```

### 2. 记忆写入+召回（memory_write_recall）

**目的**：评估记忆写入和召回的准确性

**评测流程**：
```
预期记忆 → 写入存储 → 使用问题召回 → 与预期召回记忆比较 → 计算指标
```

**使用的数据**：
- `sessions[].memories`：要写入的记忆
- `qa[].question`：召回问题
- `qa[].evidence`：预期召回的记忆ID

**支持的指标**：
- `recall_accuracy`：召回精准度
- `recall_completeness`：召回完整度

**示例**：
```bash
python3 batch_evaluation.py --scenarios memory_write_recall --metrics recall_accuracy recall_completeness
```

### 3. 对话写入+召回（conversation_write_recall）

**目的**：评估从对话提取、写入到召回的全流程效果

**评测流程**：
```
原始对话 → 提取+写入 → 使用问题召回 → 检查重复/冲突 → 计算指标
```

**使用的数据**：
- `sessions[].conversation`：原始对话
- `sessions[].memories`：预期记忆
- `qa[].question`：召回问题
- `qa[].evidence`：预期召回的记忆

**支持的指标**：
- `memory_duplication_effect`：记忆去重效果
- `memory_conflict_effect`：记忆冲突处理效果

**示例**：
```bash
python3 batch_evaluation.py --scenarios conversation_write_recall --metrics memory_duplication_effect memory_conflict_effect
```

## 评测指标

### accuracy（精准度）

**定义**：实际提取的记忆中命中预期记忆的比例

**计算公式**：
```
accuracy = 命中的记忆数 / 实际提取的记忆总数
```

**评测方式**：
- 使用 LLM 判断实际提取的记忆是否与预期记忆语义匹配
- 通过率阈值：≥ 0.6

**适用场景**：记忆提取评测（dialogue_extraction）

### completeness（完整度）

**定义**：预期记忆被实际提取覆盖的比例

**计算公式**：
```
completeness = 被覆盖的预期记忆数 / 预期记忆总数
```

**评测方式**：
- 使用 LLM 判断每条预期记忆是否被实际提取的记忆覆盖
- 通过率阈值：≥ 0.6

**适用场景**：记忆提取评测（dialogue_extraction）

### recall_accuracy（召回精准度）

**定义**：实际召回的记忆中命中预期召回记忆的比例

**计算公式**：
```
recall_accuracy = 命中的记忆数 / 实际召回的记忆总数
```

**评测方式**：
- 通过记忆 ID 精确匹配（不需要 LLM）
- 通过率阈值：≥ 0.6

**适用场景**：记忆写入+召回（memory_write_recall）

### recall_completeness（召回完整度）

**定义**：预期召回的记忆被实际召回覆盖的比例

**计算公式**：
```
recall_completeness = 被召回的预期记忆数 / 预期召回记忆总数
```

**评测方式**：
- 通过记忆 ID 精确匹配（不需要 LLM）
- 通过率阈值：≥ 0.6

**适用场景**：记忆写入+召回（memory_write_recall）

### memory_duplication_effect（记忆去重效果）

**定义**：检测召回的记忆中是否存在重复内容

**计算方式**：
```
存在重复记忆：0 分（不通过）
不存在重复记忆：1 分（通过）
没有召回任何记忆：0 分（不通过）
```

**评测方式**：
- 使用 LLM 判断召回的记忆之间是否存在语义重复
- 通过条件：score = 1.0

**适用场景**：对话写入+召回（conversation_write_recall）

### memory_conflict_effect（记忆冲突处理效果）

**定义**：检测召回的记忆中是否存在相互冲突的内容

**计算方式**：
```
存在冲突记忆：0 分（不通过）
不存在冲突记忆：1 分（通过）
没有召回任何记忆：0 分（不通过）
```

**评测方式**：
- 使用 LLM 判断召回的记忆之间是否存在语义冲突
- 通过条件：score = 1.0

**适用场景**：对话写入+召回（conversation_write_recall）

## 数据格式

### 评测数据项结构

评测数据项是评测的基本单元，采用统一的数据结构：

```json
{
  "item_name": "基础信息提取测试",
  "item_id": "test_item_001",
  "description": "测试基本的用户信息提取能力",
  "sessions": [
    {
      "sessionId": "session_001",
      "conversation": [
        {
          "messageId": "msg_001",
          "role": "user",
          "content": "你好，我叫张三",
          "chatTime": "2025-08-10 10:00:00"
        },
        {
          "messageId": "msg_002",
          "role": "assistant",
          "content": "你好张三，很高兴认识你",
          "chatTime": "2025-08-10 10:00:05"
        }
      ],
      "memories": [
        {
          "memoryId": "memory_001",
          "content": "用户叫张三",
          "metaData": {
            "source": "name_extraction",
            "confidence": 0.95
          }
        }
      ]
    }
  ],
  "qa": [
    {
      "question": "我叫什么名字？",
      "answer": "你叫张三",
      "evidence": {
        "session_001": [
          {
            "messageIds": ["msg_001"],
            "memoryIds": ["memory_001"]
          }
        ]
      }
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `item_name` | string | ✅ | 数据项名称 |
| `item_id` | string | ✅ | 数据项唯一标识 |
| `description` | string | ❌ | 数据项描述 |
| `sessions` | array | ✅ | 对话会话数组 |
| `sessions[].sessionId` | string | ✅ | 会话ID |
| `sessions[].conversation` | array | ✅ | 对话消息列表 |
| `sessions[].memories` | array | ✅ | 预期提取的记忆 |
| `qa` | array | ✅ | 问答对数组 |
| `qa[].question` | string | ✅ | 问题 |
| `qa[].answer` | string | ✅ | 答案 |
| `qa[].evidence` | object | ✅ | 证据（关联原始对话和记忆） |

### 数据复用性

同一份评测数据项可以在不同场景下复用：

- **记忆提取场景**：使用 `sessions[].conversation` 和 `sessions[].memories`
- **记忆召回场景**：使用 `sessions[].memories`、`qa[].question` 和 `qa[].evidence`
- **全流程场景**：使用所有字段

## 使用指南

### 基础用法

```bash
# 使用默认配置
python3 batch_evaluation.py

# 指定数据文件
python3 batch_evaluation.py ../data/your_test_data.json
```

### 智能场景推断

当只指定 `--metrics` 时，系统会自动推断应该评测哪些场景：

```bash
# 只评测 accuracy 和 completeness
# → 自动推断为 dialogue_extraction 场景
python3 batch_evaluation.py --metrics accuracy completeness

# 评测 accuracy 和 recall_accuracy
# → 自动推断为 dialogue_extraction 和 memory_write_recall 两个场景
python3 batch_evaluation.py --metrics accuracy recall_accuracy
```

### 手动指定场景

```bash
# 只评测记忆提取场景
python3 batch_evaluation.py --scenarios dialogue_extraction

# 评测多个场景
python3 batch_evaluation.py --scenarios dialogue_extraction memory_write_recall
```

### 组合使用

```bash
# 指定场景和指标
python3 batch_evaluation.py \
  --scenarios dialogue_extraction \
  --metrics accuracy completeness

# 指定数据文件、场景和指标
python3 batch_evaluation.py ../data/custom_data.json \
  --scenarios memory_write_recall \
  --metrics recall_accuracy recall_completeness
```

### 查看帮助

```bash
python3 batch_evaluation.py --help
```

## 扩展开发

### 添加自定义评测指标

1. 在 `evaluate/metric_evaluator.py` 中创建新的评测器类：

```python
from metric_evaluator import MetricEvaluator, register_metric

@register_metric("your_metric_name")
class YourMetricEvaluator(MetricEvaluator):
    """你的指标评测器"""
    
    def evaluate(self, expected, actual) -> MetricResult:
        # 实现你的评测逻辑
        score = self._calculate_score(expected, actual)
        
        return MetricResult(
            metric_name="your_metric_name",
            metric_value=score,
            passed=score >= 0.6,
            reason=f"评分: {score}"
        )
```

2. 在 `evaluate/scenario_factory.py` 中添加指标到相应场景：

```python
ScenarioConfig(
    scenario_name="your_scenario",
    display_name="你的场景",
    case_key="your_scenario",
    default_metrics=["your_metric_name"]  # 添加你的指标
)
```

### 添加自定义评测场景

1. 在 `evaluate/evaluation_scenario.py` 中创建新的场景类：

```python
class YourScenario(EvaluationScenario):
    """你的评测场景"""
    
    @property
    def scenario_name(self) -> str:
        return "your_scenario"
    
    @property
    def supported_metrics(self) -> List[str]:
        return ["your_metric_name"]
    
    def _prepare_data(self, case):
        # 准备数据
        pass
    
    def _run_system(self, case):
        # 运行记忆系统
        pass
    
    def _evaluate_metrics(self, case, metrics: List[str]) -> List[MetricResult]:
        # 评测指标
        pass
    
    def _collect_scenario_details(self, case) -> Dict[str, Any]:
        # 收集场景详情
        pass
```

2. 在 `evaluate/scenario_factory.py` 中注册场景：

```python
_SCENARIO_CONFIGS = {
    "your_scenario": ScenarioConfig(
        scenario_name="your_scenario",
        display_name="你的场景",
        case_key="your_scenario",
        default_metrics=["your_metric_name"]
    )
}
```

3. 在 `evaluate/evaluation_engine.py` 中注册场景实例：

```python
self.scenario_registry = {
    "your_scenario": YourScenario(
        memory_system, self.metric_registry
    )
}
```

### 扩展数据结构

在 `metaData` 字段中添加自定义元数据：

```json
{
  "memoryId": "memory_001",
  "content": "用户叫张三",
  "metaData": {
    "source": "name_extraction",
    "confidence": 0.95,
    "custom_field": "your_custom_value"
  }
}
```

## 常见问题

### Q: 如何接入自己的记忆系统？

A: 实现 `MemorySystemInterface` 接口：

```python
from memory_system_interface import MemorySystemInterface

class YourMemorySystem(MemorySystemInterface):
    def extract_memories(self, conversation, session_id):
        # 实现记忆提取
        pass
    
    def recall_memories(self, query, session_id, top_k=10):
        # 实现记忆召回
        pass
    
    def write_memories(self, memories, session_id):
        # 实现记忆写入
        pass
    
    def extract_and_write_memories(self, conversation, session_id):
        # 实现提取并写入
        pass
    
    def clear_session(self, session_id):
        # 实现会话清理
        pass
```

然后在 `batch_evaluation.py` 中替换 `MockMemorySystem`。

### Q: 为什么有些指标需要 LLM，有些不需要？

A: 
- **需要 LLM**：语义匹配类指标（如 accuracy、completeness、memory_duplication_effect、memory_conflict_effect），需要判断内容的语义相似性或冲突性
- **不需要 LLM**：ID 匹配类指标（如 recall_accuracy、recall_completeness），只需要精确匹配记忆 ID

### Q: 如何调整指标的通过阈值？

A: 在对应的评测器类中修改 `passed` 条件：

```python
return MetricResult(
    metric_name="accuracy",
    metric_value=score,
    passed=score >= 0.7,  # 修改阈值为 0.7
    reason=reason
)
```

### Q: 评测报告保存在哪里？

A: 报告保存在 `reports/` 目录下：
- JSON 报告：`reports/report_xxx.json`
- HTML 报告：`reports/report_xxx.html`

### Q: 如何查看详细的评测过程？

A: 
1. 查看控制台输出，显示每个用例的评测进度
2. 打开 HTML 报告，查看每个用例的详细信息
3. 查看 JSON 报告，获取完整的评测数据

### Q: 评测速度慢怎么办？

A: 
1. 只评测需要的指标：`--metrics accuracy`
2. 只评测需要的场景：`--scenarios dialogue_extraction`
3. 减少评测数据量
4. 优化 LLM 调用（使用更快的模型或增加并发）

## 技术支持

如有问题或建议，请提交 Issue 或 Pull Request。

## 许可证

[MIT License](LICENSE)

---

**注意**：本框架基于专利技术实现，使用时请遵守相关知识产权规定。
