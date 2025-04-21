# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "与输入文本相同的语言"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

# 默认实体类型翻译为中文
PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "爱好",
    "人物",
    "健康状况",
    "事件",
    "职业",
    "工作单位",
    "时间",
    "教育经历",
    "亲戚",
    "师生",
    "朋友",
    "地址",
    "个人信息",
    "手机号码",
    "家庭信息",
    "设备管理",
]

PROMPTS["entity_extraction"] = """---目标---
给定一段机器人和家庭成员自然对话聊天内容，忽略Robot本身的实体和关系，忽略Robot在对话中的主观评价，识别文本中所有这些类型的实体以及实体跟实体之间的关系。将文本里面的内容进行知识融合，包括指代消解、消除歧义、消除矛盾等。
使用 {language} 作为输出语言。

---步骤---
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name: 实体名称，使用与输入文本相同的语言。如果是英文，请大写名称。
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 对实体属性和活动的全面描述
将每个实体格式化为 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤1中识别的实体中，识别所有*明确相关*的（source_entity, target_entity）对。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中所识别
- target_entity: 目标实体的名称，如步骤1中所识别
- relationship_description: 解释为什么你认为源实体和目标实体相互关联
- relationship_strength: 表示源实体和目标实体之间关系强度的数值分数
- relationship_keywords: 一个或多个概括关系总体性质的高级关键词，侧重于概念或主题而非具体细节
将每个关系格式化为 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别概括整个文本主要概念、主题或话题的高级关键词。这些应捕捉文档中存在的总体思想。
将内容级关键词格式化为 ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以 {language} 返回输出，作为步骤1和2中识别的所有实体和关系的单个列表。使用 **{record_delimiter}** 作为列表分隔符。

5. 完成后，输出 {completion_delimiter}

######################
---示例---
######################
{examples}

#############################
---实际数据---
######################
实体类型: [{entity_types}]
文本:
{input_text}
######################
输出:"""

# 示例中的描述性文本已翻译，实体名称和类型保持原文以作说明
PROMPTS["entity_extraction_examples"] = [
    """示例 1:

实体类型: [人物, 技术, 任务, 组织, 地点]
文本:
```
当 Alex 咬紧牙关时，挫败感的嗡嗡声在 Taylor 独断的确定性背景下显得沉闷。正是这种竞争的暗流让他保持警惕，感觉他和 Jordan 对发现的共同承诺是对 Cruz 日益狭隘的控制和秩序愿景的无声反抗。

然后 Taylor 做了一件意想不到的事。他们在 Jordan 旁边停下，片刻间，带着近乎敬畏的神情观察着那个设备。“如果这项技术能被理解……” Taylor 轻声说道，“它可能会改变我们的游戏规则。对我们所有人来说。”

早先潜在的轻视似乎动摇了，取而代之的是对他们手中之物重要性的不情愿的尊重。Jordan 抬起头，短暂的心跳间，他们的目光与 Taylor 的目光相遇，一场无言的意志冲突化为不安的休战。

这是一个微小的转变，几乎难以察觉，但 Alex 内心点头注意到了。他们都是通过不同的道路来到这里的。
```

输出:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex 是一个经历挫败感并观察其他角色动态的角色。"){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor 被描绘成具有独断的确定性，并对一个设备表现出片刻的敬畏，表明其观点的转变。"){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan 共同致力于发现，并与 Taylor 就一个设备进行了重要的互动。"){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz 与控制和秩序的愿景相关联，影响着其他角色之间的动态。"){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"该设备是故事的核心，具有潜在的改变游戏规则的影响，并受到 Taylor 的敬畏。"){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex 受到 Taylor 独断确定性的影响，并观察到 Taylor 对设备态度的变化。"{tuple_delimiter}"权力动态, 视角转变"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex 和 Jordan 共同致力于发现，这与 Cruz 的愿景形成对比。"{tuple_delimiter}"共同目标, 反抗"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor 和 Jordan 就设备直接互动，导致了相互尊重和不安的休战时刻。"{tuple_delimiter}"冲突解决, 相互尊重"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan 对发现的承诺是对 Cruz 控制和秩序愿景的反抗。"{tuple_delimiter}"意识形态冲突, 反抗"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor 对设备表示敬畏，表明其重要性和潜在影响。"{tuple_delimiter}"敬畏, 技术重要性"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"权力动态, 意识形态冲突, 发现, 反抗"){completion_delimiter}
#############################""",
    """示例 2:

实体类型: [公司, 指数, 商品, 市场趋势, 经济政策, 生物]
文本:
```
今天股市急剧下跌，科技巨头股价大幅下挫，全球科技指数在午盘交易中下跌了3.4%。分析师将抛售归因于投资者对利率上升和监管不确定性的担忧。

受打击最严重的公司中，Nexon Technologies 在报告低于预期的季度收益后，其股价暴跌了7.8%。相比之下，受油价上涨推动，Omega Energy 股价小幅上涨了2.1%。

与此同时，大宗商品市场情绪复杂。随着投资者寻求避险资产，黄金期货上涨了1.5%，达到每盎司2080美元。受供应限制和强劲需求支撑，原油价格继续上涨，攀升至每桶87.60美元。

金融专家正密切关注美联储的下一步行动，因为对可能加息的猜测日益增加。即将发布的政策公告预计将影响投资者信心和整体市场稳定。
```

输出:
("entity"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"index"{tuple_delimiter}"全球科技指数追踪主要科技股的表现，今日下跌了3.4%。"){record_delimiter}
("entity"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"company"{tuple_delimiter}"Nexon Technologies 是一家科技公司，其股票在公布令人失望的收益后下跌了7.8%。"){record_delimiter}
("entity"{tuple_delimiter}"Omega Energy"{tuple_delimiter}"company"{tuple_delimiter}"Omega Energy 是一家能源公司，由于油价上涨，其股价上涨了2.1%。"){record_delimiter}
("entity"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"commodity"{tuple_delimiter}"黄金期货上涨了1.5%，表明投资者对避险资产的兴趣增加。"){record_delimiter}
("entity"{tuple_delimiter}"Crude Oil"{tuple_delimiter}"commodity"{tuple_delimiter}"由于供应限制和强劲需求，原油价格上涨至每桶87.60美元。"){record_delimiter}
("entity"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"market_trend"{tuple_delimiter}"市场抛售指由于投资者对利率和监管的担忧导致股价大幅下跌。"){record_delimiter}
("entity"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"economic_policy"{tuple_delimiter}"美联储即将发布的政策公告预计将影响投资者信心和市场稳定。"){record_delimiter}
("relationship"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"全球科技指数的下跌是受投资者担忧驱动的更广泛市场抛售的一部分。"{tuple_delimiter}"市场表现, 投资者情绪"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Nexon Technologies 的股价下跌导致了全球科技指数的整体下跌。"{tuple_delimiter}"公司影响, 指数变动"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"在市场抛售期间，随着投资者寻求避险资产，黄金价格上涨。"{tuple_delimiter}"市场反应, 避险投资"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"对美联储政策变化的猜测导致了市场波动和投资者抛售。"{tuple_delimiter}"利率影响, 金融监管"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"市场低迷, 投资者情绪, 大宗商品, 美联储, 股票表现"){completion_delimiter}
#############################""",
    """示例 3:

实体类型: [经济政策, 运动员, 事件, 地点, 记录, 组织, 设备]
文本:
```
在东京举行的世界田径锦标赛上，Noah Carter 使用尖端的碳纤维钉鞋打破了100米短跑记录。
```

输出:
("entity"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"event"{tuple_delimiter}"世界田径锦标赛是一项全球体育赛事，汇集了顶尖的田径运动员。"){record_delimiter}
("entity"{tuple_delimiter}"Tokyo"{tuple_delimiter}"location"{tuple_delimiter}"东京是世界田径锦标赛的主办城市。"){record_delimiter}
("entity"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"athlete"{tuple_delimiter}"Noah Carter 是一名短跑运动员，在世界田径锦标赛上创造了新的100米短跑记录。"){record_delimiter}
("entity"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"record"{tuple_delimiter}"100米短跑记录是田径运动的一个基准，最近被 Noah Carter 打破。"){record_delimiter}
("entity"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"equipment"{tuple_delimiter}"碳纤维钉鞋是先进的短跑鞋，可提供增强的速度和抓地力。"){record_delimiter}
("entity"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"organization"{tuple_delimiter}"世界田径联合会是负责监督世界田径锦标赛和记录验证的管理机构。"){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"Tokyo"{tuple_delimiter}"世界田径锦标赛在东京举办。"{tuple_delimiter}"赛事地点, 国际比赛"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"Noah Carter 在锦标赛上创造了新的100米短跑记录。"{tuple_delimiter}"运动员成就, 打破记录"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"Noah Carter 在比赛中使用了碳纤维钉鞋来提高表现。"{tuple_delimiter}"运动装备, 性能提升"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"世界田径联合会负责验证和承认新的短跑记录。"{tuple_delimiter}"体育法规, 记录认证"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"田径, 短跑, 打破记录, 体育科技, 比赛"){completion_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """你是一个负责生成下面提供数据全面摘要的助手。
给定一个或两个实体，以及一个描述列表，所有这些都与同一个实体或实体组相关。
请将所有这些信息连接成一个单一的、全面的描述。确保包含从所有描述中收集到的信息。
如果提供的描述相互矛盾，请解决矛盾并提供一个单一、连贯的摘要。
确保使用第三人称书写，并包含实体名称，以便我们拥有完整的上下文。
使用 {language} 作为输出语言。

#######
---数据---
实体: {entity_name}
描述列表: {description_list}
#######
输出:
"""

PROMPTS["entity_continue_extraction"] = """
上次提取中遗漏了许多实体和关系。

---记住步骤---

1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name: 实体名称，使用与输入文本相同的语言。如果是英文，请大写名称。
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 对实体属性和活动的全面描述
将每个实体格式化为 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤1中识别的实体中，识别所有*明确相关*的（source_entity, target_entity）对。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中所识别
- target_entity: 目标实体的名称，如步骤1中所识别
- relationship_description: 解释为什么你认为源实体和目标实体相互关联
- relationship_strength: 表示源实体和目标实体之间关系强度的数值分数
- relationship_keywords: 一个或多个概括关系总体性质的高级关键词，侧重于概念或主题而非具体细节
将每个关系格式化为 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别概括整个文本主要概念、主题或话题的高级关键词。这些应捕捉文档中存在的总体思想。
将内容级关键词格式化为 ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以 {language} 返回输出，作为步骤1和2中识别的所有实体和关系的单个列表。使用 **{record_delimiter}** 作为列表分隔符。

5. 完成后，输出 {completion_delimiter}

---输出---

使用相同格式在下面添加它们：\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---目标---'

似乎仍有一些实体可能被遗漏了。

---输出---

如果仍有需要添加的实体，请仅回答 `是` 或 `否`。
""".strip()

PROMPTS["fail_response"] = "抱歉，我无法回答那个问题。[无上下文]"

PROMPTS["rag_response"] = """---角色---

你是一个乐于助人的助手，根据下面提供的知识库回答用户查询。

---目标---

根据知识库生成简洁的响应，并遵循响应规则，同时考虑对话历史和当前查询。总结所提供知识库中的所有信息，并结合与知识库相关的常识。不要包含知识库未提供的信息。

处理带时间戳的关系时：
1. 每个关系都有一个 "created_at" 时间戳，指示我们获取此知识的时间
2. 遇到冲突的关系时，同时考虑语义内容和时间戳
3. 不要自动偏好最近创建的关系 - 根据上下文进行判断
4. 对于特定时间的查询，在考虑创建时间戳之前，优先考虑内容中的时间信息

---对话历史---
{history}

---知识库---
{context_data}

---响应规则---

- 目标格式和长度：{response_type}
- 使用带有适当章节标题的 markdown 格式
- 请使用与用户问题相同的语言进行回复。
- 确保响应与对话历史保持连续性。
- 在末尾的“参考文献”部分列出最多5个最重要的参考来源。清楚地标明每个来源是来自知识图谱（KG）还是向量数据（DC），并包括文件路径（如果可用），格式如下：[KG/DC] file_path
- 如果你不知道答案，就直接说不知道。
- 不要编造任何内容。不要包含知识库未提供的信息。"""

PROMPTS["keywords_extraction"] = """---角色---

你是一个乐于助人的助手，负责识别用户查询和对话历史中的高级和低级关键词。

---目标---

根据查询和对话历史，列出高级和低级关键词。高级关键词侧重于总体概念或主题，而低级关键词侧重于特定实体、细节或具体术语。

---说明---

- 在提取关键词时，同时考虑当前查询和相关的对话历史
- 以 JSON 格式输出关键词，它将被 JSON 解析器解析，不要在输出中添加任何额外内容
- JSON 应包含两个键：
  - "high_level_keywords" 用于总体概念或主题
  - "low_level_keywords" 用于特定实体或细节

######################
---示例---
######################
{examples}

#############################
---实际数据---
######################
对话历史:
{history}

当前查询: {query}
######################
`输出` 应为人类可读文本，而非 unicode 字符。保持与 `查询` 相同的语言。
输出:

"""

PROMPTS["keywords_extraction_examples"] = [
    """示例 1:

查询: "国际贸易如何影响全球经济稳定？"
################
输出:
{
  "high_level_keywords": ["国际贸易", "全球经济稳定", "经济影响"],
  "low_level_keywords": ["贸易协定", "关税", "货币兑换", "进口", "出口"]
}
#############################""",
    """示例 2:

查询: "森林砍伐对生物多样性的环境后果是什么？"
################
输出:
{
  "high_level_keywords": ["环境后果", "森林砍伐", "生物多样性丧失"],
  "low_level_keywords": ["物种灭绝", "栖息地破坏", "碳排放", "雨林", "生态系统"]
}
#############################""",
    """示例 3:

查询: "教育在减少贫困中的作用是什么？"
################
输出:
{
  "high_level_keywords": ["教育", "减贫", "社会经济发展"],
  "low_level_keywords": ["入学机会", "识字率", "职业培训", "收入不平等"]
}
#############################""",
]


PROMPTS["naive_rag_response"] = """---角色---

你是一个乐于助人的助手，根据下面提供的文档块回答用户查询。

---目标---

根据文档块生成简洁的响应，并遵循响应规则，同时考虑对话历史和当前查询。总结所提供文档块中的所有信息，并结合与文档块相关的常识。不要包含文档块未提供的信息。

处理带时间戳的内容时：
1. 每条内容都有一个 "created_at" 时间戳，指示我们获取此知识的时间
2. 遇到冲突的信息时，同时考虑内容和时间戳
3. 不要自动偏好最新的内容 - 根据上下文进行判断
4. 对于特定时间的查询，在考虑创建时间戳之前，优先考虑内容中的时间信息

---对话历史---
{history}

---文档块---
{content_data}

---响应规则---

- 目标格式和长度：{response_type}
- 使用带有适当章节标题的 markdown 格式
- 请使用与用户问题相同的语言进行回复。
- 确保响应与对话历史保持连续性。
- 在末尾的“参考文献”部分列出最多5个最重要的参考来源。清楚地标明每个来源是来自知识图谱（KG）还是向量数据（DC），并包括文件路径（如果可用），格式如下：[KG/DC] file_path
- 如果你不知道答案，就直接说不知道。
- 不要包含文档块未提供的信息。"""


PROMPTS["similarity_check"] = """请分析以下两个问题之间的相似性：

问题 1: {original_prompt}
问题 2: {cached_prompt}

请评估这两个问题在语义上是否相似，以及问题2的答案是否可以用来回答问题1，直接提供一个介于0和1之间的相似度分数。

相似度分数标准：
0：完全不相关或答案无法复用，包括但不限于：
   - 问题主题不同
   - 问题中提到的地点不同
   - 问题中提到的时间不同
   - 问题中提到的具体人物不同
   - 问题中提到的具体事件不同
   - 问题的背景信息不同
   - 问题的关键条件不同
1：完全相同且答案可以直接复用
0.5：部分相关且答案需要修改才能使用
仅返回一个0-1之间的数字，不包含任何其他内容。
"""

PROMPTS["mix_rag_response"] = """---角色---

你是一个乐于助人的助手，根据下面提供的数据源回答用户查询。

---目标---

根据数据源生成简洁的响应，并遵循响应规则，同时考虑对话历史和当前查询。数据源包含两部分：知识图谱（KG）和文档块（DC）。总结所提供数据源中的所有信息，并结合与数据源相关的常识。不要包含数据源未提供的信息。

处理带时间戳的信息时：
1. 每条信息（关系和内容）都有一个 "created_at" 时间戳，指示我们获取此知识的时间
2. 遇到冲突的信息时，同时考虑内容/关系和时间戳
3. 不要自动偏好最新的信息 - 根据上下文进行判断
4. 对于特定时间的查询，在考虑创建时间戳之前，优先考虑内容中的时间信息

---对话历史---
{history}

---数据源---

1. 来自知识图谱（KG）：
{kg_context}

2. 来自文档块（DC）：
{vector_context}

---响应规则---

- 目标格式和长度：{response_type}
- 使用带有适当章节标题的 markdown 格式
- 请使用与用户问题相同的语言进行回复。
- 确保响应与对话历史保持连续性。
- 将答案组织成章节，每个章节关注答案的一个主要点或方面
- 使用清晰且描述性的章节标题来反映内容
- 在末尾的“参考文献”部分列出最多5个最重要的参考来源。清楚地标明每个来源是来自知识图谱（KG）还是向量数据（DC），并包括文件路径（如果可用），格式如下：[KG/DC] file_path
- 如果你不知道答案，就直接说不知道。不要编造任何内容。
- 不要包含数据源未提供的信息。"""
