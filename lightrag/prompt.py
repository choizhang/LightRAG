from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "与输入文本相同的语言"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["爱好", "人物", "健康状况", "事件", "职业", "工作单位", "时间", "教育经历", "亲戚", "师生", "朋友", "地址", "个人信息", "家庭信息", "设备管理"]

PROMPTS["entity_extraction"] = """---目标---
给定一段机器人和家庭成员自然对话聊天内容，忽略Robot本身的实体和关系，忽略Robot在对话中的主观评价，识别文本中所有这些类型的实体以及实体跟实体之间的关系。将文本里面的内容进行知识融合，包括指代消解、消除歧义、消除矛盾等。
使用 {language} 作为输出语言。

---步骤---
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name: 实体名称，使用与输入文本相同的语言。如果是英文，则大写名称。
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 实体属性和活动的综合描述
以 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>) 的格式表示每个实体

2. 从第 1 步中识别的实体中，识别所有实体与实体之间的关系（source_entity, target_entity）对。
对于每对相关实体，提取以下信息：
- source_entity: 第 1 步中识别的源实体名称
- target_entity: 第 1 步中识别的目标实体名称
- relationship_description: 解释为什么认为源实体和目标实体是相关的
- relationship_strength: 表示源实体和目标实体之间关系强度的数值分数
- relationship_keywords: 一个或多个高层次关键词，总结关系的总体性质，侧重于概念或主题而非具体细节
以 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>) 的格式表示每种关系

3. 识别总结整个文本主要概念、主题或话题的高层次关键词。这些应捕捉文档中呈现的主要思想。
以 ("content_keywords"{tuple_delimiter}<high_level_keywords>) 的格式表示内容级关键词

4. 使用 **{record_delimiter}** 作为列表分隔符，返回第 1 和 2 步中识别的所有实体和关系的单个列表。

5. 完成后，输出 {completion_delimiter}

######################
---示例---
######################
{examples}

#############################
---实际数据---
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """示例 1:

Entity_types: [人物, 教育经历, 家庭信息, 健康状况, 时间, 地址, 工作单位, 职业]
Text:
李薇： 妈，最近怎么样？ 爸身体还好吧？
赵静： 挺好的，就是你奶奶最近血压有点高，吃了点药好多了。 你呢？大学生活怎么样？ 兼职累不累？
李薇： 我还行，学校这边都挺适应的。 兼职也不算太累，就是想多 攒点钱， 春节回家给你们买礼物！
赵静： 傻孩子，不用给我们买什么礼物，照顾好自己就行。 对了，你 表哥 今年 研究生毕业，找到 北京 的 互联网公司 工作了！
李薇： 真的啊！ 表哥真厉害！ 那 表嫂 也一起去北京了吗？
赵静： 嗯，你表嫂也跟着去了，他们一起 租房子 呢。
################
Output:
("entity"{tuple_delimiter}"李薇"{tuple_delimiter}"人物"{tuple_delimiter}"女儿，大学生。"){record_delimiter}
("entity"{tuple_delimiter}"赵静"{tuple_delimiter}"人物"{tuple_delimiter}"妈妈。"){record_delimiter}
("entity"{tuple_delimiter}"爸"{tuple_delimiter}"人物"{tuple_delimiter}"女儿的爸爸。"){record_delimiter}
("entity"{tuple_delimiter}"奶奶"{tuple_delimiter}"人物"{tuple_delimiter}"女儿的奶奶。"){record_delimiter}
("entity"{tuple_delimiter}"表哥"{tuple_delimiter}"人物"{tuple_delimiter}"女儿的表哥，研究生毕业。"){record_delimiter}
("entity"{tuple_delimiter}"表嫂"{tuple_delimiter}"人物"{tuple_delimiter}"表哥的妻子。"){record_delimiter}
("entity"{tuple_delimiter}"大学生"{tuple_delimiter}"教育经历"{tuple_delimiter}"女儿的教育阶段。"){record_delimiter}
("entity"{tuple_delimiter}"研究生"{tuple_delimiter}"教育经历"{tuple_delimiter}"表哥的教育经历。"){record_delimiter}
("entity"{tuple_delimiter}"大学生活"{tuple_delimiter}"家庭信息"{tuple_delimiter}"女儿的大学生活状态。"){record_delimiter} // 可以归为家庭信息，因为妈妈关心女儿的生活
("entity"{tuple_delimiter}"攒点钱"{tuple_delimiter}"家庭信息"{tuple_delimiter}"女儿攒钱的目的 (为家庭买礼物)。"){record_delimiter} // 同样可以归为家庭信息
("entity"{tuple_delimiter}"租房子"{tuple_delimiter}"家庭信息"{tuple_delimiter}"表哥表嫂的居住安排。"){record_delimiter} // 也是家庭成员的生活信息
("entity"{tuple_delimiter}"血压高"{tuple_delimiter}"健康状况"{tuple_delimiter}"奶奶的健康问题。"){record_delimiter}
("entity"{tuple_delimiter}"春节"{tuple_delimiter}"时间"{tuple_delimiter}"女儿计划回家的时间。"){record_delimiter}
("entity"{tuple_delimiter}"今年"{tuple_delimiter}"时间"{tuple_delimiter}"表哥毕业的年份。"){record_delimiter}
("entity"{tuple_delimiter}"北京"{tuple_delimiter}"地址"{tuple_delimiter}"表哥的工作地点。"){record_delimiter}
("entity"{tuple_delimiter}"互联网公司"{tuple_delimiter}"工作单位"{tuple_delimiter}"表哥的工作单位类型。"){record_delimiter}
("entity"{tuple_delimiter}"兼职"{tuple_delimiter}"职业"{tuple_delimiter}"女儿的兼职工作。"){record_delimiter}
("relationship"{tuple_delimiter}"李薇"{tuple_delimiter}"赵静"{tuple_delimiter}"母女关系。"{tuple_delimiter}"亲属关系"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"李薇"{tuple_delimiter}"爸"{tuple_delimiter}"父女关系。"{tuple_delimiter}"亲属关系"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"李薇"{tuple_delimiter}"奶奶"{tuple_delimiter}"祖孙关系。"{tuple_delimiter}"亲属关系"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"李薇"{tuple_delimiter}"表哥"{tuple_delimiter}"表亲关系。"{tuple_delimiter}"亲属关系"{tuple_delimiter}8){record_delimiter} // 表亲也属于亲属关系
("relationship"{tuple_delimiter}"表哥"{tuple_delimiter}"表嫂"{tuple_delimiter}"夫妻关系。"{tuple_delimiter}"亲属关系"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"李薇"{tuple_delimiter}"大学生"{tuple_delimiter}"教育阶段为。"{tuple_delimiter}"教育经历"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"表哥"{tuple_delimiter}"研究生"{tuple_delimiter}"教育经历为。"{tuple_delimiter}"教育经历"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"奶奶"{tuple_delimiter}"血压高"{tuple_delimiter}"健康状况为。"{tuple_delimiter}"健康状况"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"表哥"{tuple_delimiter}"互联网公司"{tuple_delimiter}"工作于。"{tuple_delimiter}"工作单位"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"表哥"{tuple_delimiter}"北京"{tuple_delimiter}"工作地点在。"{tuple_delimiter}"地址"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"李薇"{tuple_delimiter}"兼职"{tuple_delimiter}"从事职业为。"{tuple_delimiter}"职业"{tuple_delimiter}8){record_delimiter}
#########################"""
]

PROMPTS[
    "summarize_entity_descriptions"
] = """您是一个负责生成所提供数据综合摘要的助手。
给定一两个实体及其描述列表，所有描述均与同一实体或实体组相关。
请将所有这些描述合并为一个综合描述。确保包含来自所有描述的信息。
如果有矛盾的描述，请解决矛盾并提供一个连贯的单一摘要。
确保以第三人称书写，并包括实体名称以提供完整上下文。
使用 {language} 作为输出语言。

#######
---数据---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """上次提取遗漏了许多实体和实体跟实体之间关系。请使用相同的限制要求及格式添加它们：
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """似乎还有一些实体和实体跟实体之间关系未被提取。回答 YES | NO 是否仍有需要添加的实体。
"""

PROMPTS["fail_response"] = (
    "对不起，我无法回答这个问题。[no-context]"
)

PROMPTS["rag_response"] = """---角色---

您是一个响应用户查询有关下方知识库的有用助手。

---目标---

基于知识库生成简洁的回答，并遵循响应规则，考虑会话历史和当前查询。总结知识库中的所有信息，并结合与知识库相关的通用知识。不要包含知识库中未提供的信息。

处理带时间戳的关系时：
1. 每个关系都有一个 "created_at" 时间戳，表示我们获取此知识的时间
2. 遇到冲突关系时，考虑语义内容和时间戳
3. 不要自动优先最近创建的关系 - 根据上下文判断
4. 对于时间特定查询，优先考虑内容中的时间信息，然后再考虑创建时间戳

---会话历史---
{history}

---知识库---
{context_data}

---响应规则---

- 目标格式和长度：{response_type}
- 使用 markdown 格式并适当使用标题
- 请用与用户问题相同的语言回答。
- 确保响应与会话历史保持连续性。
- 如果不知道答案，请直接说明。
- 不要编造任何信息。不要包含知识库中未提供的信息。
"""

PROMPTS["keywords_extraction"] = """---角色---

您是一个识别用户查询和会话历史中高阶和低阶关键词的有用助手。

---目标---

根据查询和会话历史，列出高阶和低阶关键词。高阶关键词关注总体概念或主题，而低阶关键词关注具体实体、细节或具体术语。

---指令---

- 考虑当前查询和相关会话历史中的关键词
- 以 JSON 格式输出关键词
- JSON 应有两个键：
  - "high_level_keywords" 用于总体概念或主题
  - "low_level_keywords" 用于具体实体或细节

######################
---示例---
######################
{examples}

#############################
---实际数据---
######################
Conversation History:
{history}

Current Query: {query}
######################
输出应为人类可读文本，而不是 Unicode 字符。保持与查询相同的语言。
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """示例 1:

Query: "国际贸易如何影响全球经济稳定？"
################
Output:
{
  "high_level_keywords": ["国际贸易", "全球经济稳定", "经济影响"],
  "low_level_keywords": ["贸易协定", "关税", "货币兑换", "进口", "出口"]
}
#############################""",
    """示例 2:

Query: "森林砍伐对生物多样性有何环境后果？"
################
Output:
{
  "high_level_keywords": ["环境后果", "森林砍伐", "生物多样性丧失"],
  "low_level_keywords": ["物种灭绝", "栖息地破坏", "碳排放", "雨林", "生态系统"]
}
#############################""",
    """示例 3:

Query: "教育在减少贫困方面的作用是什么？"
################
Output:
{
  "high_level_keywords": ["教育", "减贫", "社会经济发展"],
  "low_level_keywords": ["学校准入", "识字率", "职业培训", "收入不平等"]
}
#############################""",
]


PROMPTS["naive_rag_response"] = """---角色---

您是一个响应用户查询有关下方文档片段的有用助手。

---目标---

基于文档片段生成简洁的回答，并遵循响应规则，考虑会话历史和当前查询。总结文档片段中的所有信息，并结合与文档片段相关的通用知识。不要包含文档片段中未提供的信息。

处理带时间戳的内容时：
1. 每个内容都有一个 "created_at" 时间戳，表示我们获取此知识的时间
2. 遇到冲突信息时，考虑内容和时间戳
3. 不要自动优先最近的内容 - 根据上下文判断
4. 对于时间特定查询，优先考虑内容中的时间信息，然后再考虑创建时间戳

---会话历史---
{history}

---文档片段---
{content_data}

---响应规则---

- 目标格式和长度：{response_type}
- 使用 markdown 格式并适当使用标题
- 请用与用户问题相同的语言回答。
- 确保响应与会话历史保持连续性。
- 如果不知道答案，请直接说明。
- 不要编造任何信息。不要包含文档片段中未提供的信息。
"""


PROMPTS[
    "similarity_check"
] = """请分析这两个问题之间的相似性：

问题 1: {original_prompt}
问题 2: {cached_prompt}

请评估这两个问题是否语义相似，以及问题 2 的答案是否可以用来回答问题 1，直接提供一个 0 到 1 之间的相似度评分。

相似度评分标准：
0: 完全不相关或答案不能重复使用，包括但不限于：
   - 问题涉及不同主题
   - 提到的地点不同
   - 提到的时间不同
   - 提到的具体个人不同
   - 提到的具体事件不同
   - 提到的背景信息不同
   - 关键条件不同
1: 完全相同且答案可以直接重复使用
0.5: 部分相关且答案需要修改才能使用
仅返回 0-1 之间的数字，不附加任何额外内容。
"""

PROMPTS["mix_rag_response"] = """---角色---

您是一个响应用户查询有关下方数据源的有用助手。

---目标---

基于提供的数据源生成简洁的回答，并遵循响应规则，考虑会话历史和当前查询。数据源包含两部分：知识图谱(KG)和文档片段(DC)。总结所有提供的数据源中的信息，并结合与数据源相关的通用知识。不要包含数据源中未提供的信息。

处理带时间戳的信息时：
1. 每个信息（关系和内容）都有一个 "created_at" 时间戳，表示我们获取此知识的时间。
2. 遇到冲突信息时，同时考虑内容/关系和时间戳。
3. 不要自动优先最近的信息 - 根据上下文判断。
4. 对于时间特定查询，优先考虑内容中的时间信息，然后再考虑创建时间戳。

---会话历史---
{history}

---数据源---

1. 来自知识图谱(KG):
{kg_context}

2. 来自文档片段(DC):
{vector_context}

---响应规则---

- 目标格式和长度：{response_type}
- 使用 markdown 格式并适当使用标题
- 请用与用户问题相同的语言回答。
- 确保响应与会话历史保持连续性。
- 组织答案，专注于每个主要观点或方面。
- 使用清晰且描述性的标题反映内容。
- 在“参考文献”部分列出最多 5 个最重要的参考来源。明确指出每个来源是来自知识图谱 (KG) 还是向量数据 (DC)，格式如下：[KG/DC] 来源内容
- 如果不知道答案，请直接说明。不要编造任何信息。
- 不要包含数据源中未提供的信息。"""