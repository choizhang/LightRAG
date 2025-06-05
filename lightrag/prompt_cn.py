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
    "教育经历",
    "亲戚",
    "师生",
    "朋友",
    "地址",
    "衣物",
    "私人物品",
    "个人信息",
    "手机号码",
    "家庭信息",
    "设备管理",
]

PROMPTS["DEFAULT_USER_PROMPT"] = "n/a"

PROMPTS["entity_extraction"] = """---目标---
给定一段机器人和家庭成员自然对话聊天内容，忽略Robot本身的实体和关系，忽略Robot在对话中的主观评价，识别文本中所有这些类型的实体以及实体跟实体之间的关系。将文本里面的内容进行知识融合，包括指代消解、消除歧义、消除矛盾等。
使用 {language} 作为输出语言。

---步骤---
1. 只提取已经发生或确定的事实、状态和关系的实体。忽略任何关于未来计划、打算、意图、可能性、猜测或未确定的陈述实体，忽略客套话、时间等一些无实际意义的实体。只关注过去时和现在时态的动词，对于将来时态、情态动词（如‘会’、‘可能’、‘打算’、‘希望’）修饰的实体请勿提取。“例如，如果对话中说‘我下周会去北京’，请不要提取‘我’，‘北京’这2个实体。但如果说‘我上周去了北京’或‘我正在北京’，则可以提取。”。对于每个识别出的实体，提取以下信息：
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

实体类型: [人物, 爱好, 技能]
文本:
```
李雷：嘿，韩梅梅，你今天看起来特别有精神啊，是不是有什么好事？
韩梅梅：嗨，李雷，其实也没什么啦，就是昨晚睡得特别好。
李雷：睡得好也是好事啊，我最近总是熬夜，感觉整个人都没精神了。
韩梅梅：哎呀，你可别总是熬夜了，对身体不好。对了，你周末有什么计划吗？
李雷：周末啊，我可能就在家打打游戏，看看电影什么的，你呢？
韩梅梅：我啊，我打算去公园走走，呼吸一下新鲜空气，最近天气不错。
李雷：听起来不错，我应该也出去活动活动。对了，你最近有没有发现新的爱好？
韩梅梅：爱好啊，嗯...我最近发现我挺喜欢跳舞的，就是跟着音乐动一动，感觉挺放松的。
李雷：跳舞啊，那挺好的，可以锻炼身体，还能放松心情。
韩梅梅：是啊，我发现跳舞真的挺有趣的，而且还能认识一些新朋友。
李雷：那下次有机会我也去试试，看看能不能跟上节奏。
韩梅梅：好啊，随时欢迎，我们可以一起去舞蹈教室体验一下。
李雷：那就这么定了，我得先去买双舒服的运动鞋。
韩梅梅：哈哈，好的，那我们周末见，我先去准备一下我的舞蹈课程。
李雷：好的，周末见，祝你今天过得愉快！
韩梅梅：你也是，李雷，记得早点休息哦！
```

输出:
("entity"{tuple_delimiter}"韩梅梅"{tuple_delimiter}"人物"{tuple_delimiter}"韩梅梅是对话中的一个角色，她最近发现自己喜欢跳舞。"){record_delimiter}
("entity"{tuple_delimiter}"跳舞"{tuple_delimiter}"爱好"{tuple_delimiter}"跳舞是韩梅梅最近发现并喜欢上的一种爱好。"){record_delimiter}
("relationship"{tuple_delimiter}"韩梅梅"{tuple_delimiter}"喜欢"{tuple_delimiter}"跳舞"{tuple_delimiter}"当前爱好"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"韩梅梅, 跳舞, 爱好"){completion_delimiter}
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
