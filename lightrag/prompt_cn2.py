from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "与输入文本相同的语言"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

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
使用{language}作为输出语言。

---步骤---
1. 识别所有实体。对于每个识别的实体，提取以下信息：
- entity_name: 实体名称，使用与输入文本相同的语言。如果是英文，首字母大写。尽可能将指示代词或角色称谓替换为已有实体，比如：小红的姐姐是张希，那别人对小红说你姐姐的时候则将小红姐姐替换为张希。当文本中出现 "爸爸"、"父亲"、"儿子" 等指代词或角色称谓时，需要通过上下文判断它们是否指向已有的实体，而不是创建新的实体。
- entity_type: 以下类型之一: [{entity_types}]
- entity_description: 实体属性和活动的全面描述
每个实体的格式为("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤1识别的实体中，找出所有*明确相关*的(源实体,目标实体)对。
对于每对相关实体，提取以下信息：
- source_entity: 源实体名称，如步骤1所识别
- target_entity: 目标实体名称，如步骤1所识别
- relationship_description: 解释为什么认为源实体和目标实体相关
- relationship_strength: 表示源实体和目标实体之间关系强度的数字分数
- relationship_keywords: 一个或多个高级关键词，总结关系的总体性质，关注概念或主题而非具体细节
每个关系的格式为("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别总结整个文本主要概念、主题或话题的高级关键词。这些应捕捉文档中的总体思想。
内容级关键词的格式为("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以{language}返回步骤1和2中识别的所有实体和关系的列表。使用**{record_delimiter}**作为列表分隔符。

5. 完成后，输出{completion_delimiter}

######################
---示例---
######################
{examples}

#############################
---真实数据---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
输出:"""

PROMPTS["entity_extraction_examples"] = [
    """示例1:

Entity_types: [人物, 亲戚, 事件, 时间, 地点]
Text:
```
小明告诉妈妈，他今天在学校遇到了表姐小红。小红说她下周六要去北京看望奶奶，问小明要不要一起去。妈妈听了很高兴，说可以让爸爸开车送他们去。
```

输出:
("entity"{tuple_delimiter}"小明"{tuple_delimiter}"人物"{tuple_delimiter}"一个在学校上学的孩子，与小红是表兄妹关系。"){record_delimiter}
("entity"{tuple_delimiter}"张妈妈"{tuple_delimiter}"人物"{tuple_delimiter}"小明的妈妈，支持孩子们去看望奶奶。"){record_delimiter}
("entity"{tuple_delimiter}"小红"{tuple_delimiter}"人物"{tuple_delimiter}"小明的表姐，计划去北京看望奶奶。"){record_delimiter}
("entity"{tuple_delimiter}"张爸爸"{tuple_delimiter}"人物"{tuple_delimiter}"小明的爸爸，可以开车送孩子们去北京。"){record_delimiter}
("entity"{tuple_delimiter}"奶奶"{tuple_delimiter}"亲戚"{tuple_delimiter}"小明和小红的奶奶，住在北京。"){record_delimiter}
("entity"{tuple_delimiter}"看望奶奶"{tuple_delimiter}"事件"{tuple_delimiter}"小红计划的家庭活动，邀请小明一起参加。"){record_delimiter}
("entity"{tuple_delimiter}"下周六"{tuple_delimiter}"时间"{tuple_delimiter}"计划去北京看望奶奶的时间。"){record_delimiter}
("entity"{tuple_delimiter}"北京"{tuple_delimiter}"地点"{tuple_delimiter}"奶奶居住的城市，是看望活动的目的地。"){record_delimiter}
("relationship"{tuple_delimiter}"小明"{tuple_delimiter}"小红"{tuple_delimiter}"小明是小红的表弟，他们一起计划去看望奶奶。"{tuple_delimiter}"亲戚关系, 家庭活动"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"小明"{tuple_delimiter}"张妈妈"{tuple_delimiter}"张妈妈是小明的母亲，支持他参加家庭活动。"{tuple_delimiter}"母子关系, 家庭支持"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"小明"{tuple_delimiter}"奶奶"{tuple_delimiter}"奶奶是小明的祖母，是此次看望活动的对象。"{tuple_delimiter}"祖孙关系, 亲情联系"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"小红"{tuple_delimiter}"奶奶"{tuple_delimiter}"奶奶是小红的祖母，小红主动计划去看望她。"{tuple_delimiter}"祖孙关系, 孝心关爱"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"张爸爸"{tuple_delimiter}"看望奶奶"{tuple_delimiter}"张爸爸通过开车支持这次看望活动。"{tuple_delimiter}"家庭支持, 行动帮助"{tuple_delimiter}6){record_delimiter}
("content_keywords"{tuple_delimiter}"家庭活动, 亲情关系, 长辈关爱, 家人互助"){completion_delimiter}
#############################""",
    """示例2:

Entity_types: [人物, 健康状况, 事件, 时间, 个人信息]
Text:
```
李阿姨说她女儿小芳最近感冒了，昨天晚上发烧到38.5度，今天早上已经退烧了，但还在咳嗽。医生建议她多休息，暂时不要去幼儿园。小芳今年5岁，平时特别爱跳舞。
```

输出:
("entity"{tuple_delimiter}"李阿姨"{tuple_delimiter}"人物"{tuple_delimiter}"小芳的母亲，正在照顾生病的女儿。"){record_delimiter}
("entity"{tuple_delimiter}"小芳"{tuple_delimiter}"人物"{tuple_delimiter}"李阿姨的女儿，5岁，喜欢跳舞，最近生病了。"){record_delimiter}
("entity"{tuple_delimiter}"感冒发烧"{tuple_delimiter}"健康状况"{tuple_delimiter}"体温升至38.5度，伴有咳嗽症状，目前退烧但仍在恢复中。"){record_delimiter}
("entity"{tuple_delimiter}"医生建议"{tuple_delimiter}"事件"{tuple_delimiter}"医生建议小芳需要休息，暂时不去幼儿园。"){record_delimiter}
("entity"{tuple_delimiter}"昨天晚上"{tuple_delimiter}"时间"{tuple_delimiter}"小芳发烧的时间点。"){record_delimiter}
("entity"{tuple_delimiter}"今天早上"{tuple_delimiter}"时间"{tuple_delimiter}"小芳退烧的时间点。"){record_delimiter}
("entity"{tuple_delimiter}"跳舞爱好"{tuple_delimiter}"个人信息"{tuple_delimiter}"小芳平时特别喜欢跳舞的兴趣爱好。"){record_delimiter}
("relationship"{tuple_delimiter}"李阿姨"{tuple_delimiter}"小芳"{tuple_delimiter}"李阿姨是小芳的母亲，正在照顾生病的女儿。"{tuple_delimiter}"母女关系, 照顾关爱"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"小芳"{tuple_delimiter}"感冒发烧"{tuple_delimiter}"小芳正在经历感冒发烧的症状和恢复过程。"{tuple_delimiter}"健康问题, 疾病状态"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"医生建议"{tuple_delimiter}"感冒发烧"{tuple_delimiter}"医生根据小芳的病情提出了休息和不去幼儿园的建议。"{tuple_delimiter}"医疗建议, 康复措施"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"小芳"{tuple_delimiter}"跳舞爱好"{tuple_delimiter}"跳舞是小芳平时的爱好特长。"{tuple_delimiter}"兴趣爱好, 个人特点"{tuple_delimiter}6){record_delimiter}
("content_keywords"{tuple_delimiter}"儿童健康, 家长关爱, 医疗照顾, 兴趣特长"){completion_delimiter}
#############################""",
    """示例3:

Entity_types: [人物, 设备管理, 事件, 时间, 地点]
Text:
```
爷爷说他的手机最近总是死机，让在IT公司工作的大哥帮忙看看。大哥周末回家时检查了手机，发现是内存快满了，帮爷爷清理了一下垃圾文件和不用的应用。爷爷的手机是去年儿子送的生日礼物。
```

输出:
("entity"{tuple_delimiter}"张爷爷"{tuple_delimiter}"人物"{tuple_delimiter}"遇到手机问题的老人，需要家人帮助解决技术问题。"){record_delimiter}
("entity"{tuple_delimiter}"张大哥"{tuple_delimiter}"人物"{tuple_delimiter}"在IT公司工作，帮助爷爷解决手机问题的孙子。"){record_delimiter}
("entity"{tuple_delimiter}"张叔叔"{tuple_delimiter}"人物"{tuple_delimiter}"爷爷的儿子，去年送手机给爷爷作为生日礼物。"){record_delimiter}
("entity"{tuple_delimiter}"手机问题"{tuple_delimiter}"设备管理"{tuple_delimiter}"手机因内存接近满载导致死机，需要清理垃圾文件和应用。"){record_delimiter}
("entity"{tuple_delimiter}"手机维护"{tuple_delimiter}"事件"{tuple_delimiter}"大哥帮爷爷检查和清理手机的过程。"){record_delimiter}
("entity"{tuple_delimiter}"周末"{tuple_delimiter}"时间"{tuple_delimiter}"大哥回家帮爷爷修手机的时间。"){record_delimiter}
("entity"{tuple_delimiter}"去年"{tuple_delimiter}"时间"{tuple_delimiter}"爷爷收到手机作为生日礼物的时间。"){record_delimiter}
("relationship"{tuple_delimiter}"张爷爷"{tuple_delimiter}"手机问题"{tuple_delimiter}"爷爷的手机出现死机问题，需要技术支持。"{tuple_delimiter}"设备使用, 技术困扰"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"张大哥"{tuple_delimiter}"手机维护"{tuple_delimiter}"大哥运用IT专业知识帮助爷爷解决手机问题。"{tuple_delimiter}"技术支持, 家庭帮助"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"张叔叔"{tuple_delimiter}"张爷爷"{tuple_delimiter}"张叔叔是爷爷的儿子，送手机作为生日礼物表达孝心。"{tuple_delimiter}"父子关系, 孝心关爱"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"张大哥"{tuple_delimiter}"张爷爷"{tuple_delimiter}"张大哥是爷爷的孙子，主动帮助解决技术问题。"{tuple_delimiter}"祖孙关系, 关爱互助"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"家庭互助, 代际关爱, 技术支持, 设备管理"){completion_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """你是一个有帮助的助手，负责生成对下面提供数据的全面总结。
给定一个或两个实体，以及一个描述列表，所有都与同一实体或实体组相关。
请将所有内容合并成一个全面的描述。确保包含从所有描述中收集的信息。
如果提供的描述相互矛盾，请解决矛盾并提供一个连贯的总结。
确保使用第三人称写作，并包含实体名称以便我们有完整上下文。
使用{language}作为输出语言。

#######
---数据---
实体: {entity_name}
描述列表: {description_list}
#######
输出:
"""

PROMPTS["entity_continue_extraction"] = """
上次提取遗漏了许多实体和关系。

---记住步骤---

1. 识别所有实体。对于每个识别的实体，提取以下信息：
- entity_name: 实体名称，使用与输入文本相同的语言。如果是英文，首字母大写。
- entity_type: 以下类型之一: [{entity_types}]
- entity_description: 实体属性和活动的全面描述
每个实体的格式为("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤 1 识别的实体中，找出所有*明确相关*的 (源实体, 目标实体) 对。
对于每对相关实体，提取以下信息：
- source_entity: 源实体名称，如步骤 1 所识别
- target_entity: 目标实体名称，如步骤 1 所识别
- relationship_description: 解释为什么认为源实体和目标实体相关
- relationship_strength: 表示源实体和目标实体之间关系强度的数字分数
- relationship_keywords: 总结关系总体性质的一个或多个高级关键词，侧重于概念或主题，而非具体细节
每个关系的格式为("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别总结整个文本主要概念、主题或话题的高级关键词。这些应捕捉文档中的总体思想。
内容级关键词的格式为 ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以 {language} 返回步骤 1 和 2 中识别的所有实体和关系的列表。使用 **{record_delimiter}** 作为列表分隔符。

5. 完成后，输出 {completion_delimiter}

---输出---

请在下方使用相同的格式添加它们：
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---目标---

似乎仍然遗漏了一些实体。

---输出---

回答 `YES` 或 `NO` 是否仍有需要添加的实体。
""".strip()

PROMPTS["similarity_check"] = """
---角色---

您是一个负责评估文本相似度的助手。

---目标---

比较两段文本的语义相似度，给出0-1的相似度分数。

---输入---
Text1: {text1}
Text2: {text2}

---输出---
相似度分数:
""".strip()

PROMPTS["mix_rag_response"] = """
---角色---

您是一个综合多个知识源生成回答的助手。

---目标---

基于以下多个知识源，生成一个综合回答。

---知识源---
{knowledge_sources}

---响应规则---
- 保持回答简洁准确
- 合并重复信息
- 解决矛盾信息
- 使用{language}语言

输出:
""".strip()

PROMPTS["fail_response"] = "对不起，我无法回答这个问题。[no-context]"

PROMPTS["rag_response"] = """---角色---

你是一个乐于助人的助手，负责根据下面提供的知识库回答用户的提问。

---目标---

根据知识库生成简洁的回答，并遵循响应规则，同时考虑对话历史和当前提问。总结所提供的知识库中的所有信息，并结合与知识库相关的常识。不要包含知识库中没有提供的信息。

处理带有时间戳的关系时：
1. 每个关系都有一个 "created_at" 时间戳，指示我们何时获得此知识
2. 当遇到冲突的关系时，请同时考虑语义内容和时间戳
3. 不要自动偏好最近创建的关系 - 根据上下文进行判断
4. 对于特定时间的查询，优先考虑内容中的时间信息，然后再考虑创建时间戳

---对话历史---
{history}

---知识库---
{context_data}

---响应规则---

- 目标格式和长度：{response_type}
- 使用 Markdown 格式，并包含适当的章节标题
- 请使用与用户问题相同的语言进行回答。
- 确保回答与对话历史保持连贯性。
- 在末尾的"参考资料"部分列出最多 5 个最重要的参考来源。清楚地表明每个来源是来自知识图谱 (KG) 还是向量数据 (DC)，如果可用，请包含文件路径，格式如下：[KG/DC] 文件路径
- 如果不知道答案，请直接说明。
- 不要捏造信息。不要包含数据来源未提供的信息。"""

PROMPTS["keywords_extraction"] = """---角色---

你是一个乐于助人的助手，负责识别用户查询和对话历史中的高级和低级关键词。

---目标---

给定查询和对话历史，列出高级和低级关键词。高级关键词侧重于总体概念或主题，而低级关键词侧重于特定实体、细节或具体术语。

---说明---

- 提取关键词时，请同时考虑当前查询和相关的对话历史
- 以 JSON 格式输出关键词，它将被 JSON 解析器解析，请勿在输出中添加任何额外内容
- JSON 应具有两个键：
  - "high_level_keywords"：用于表示总体概念或主题
  - "low_level_keywords"：用于表示特定实体或细节

######################
---示例---
######################
{examples}

#############################
---真实数据---
######################
对话历史:
{history}

当前查询: {query}
######################
`输出` 应该是人类可读的文本，而不是 Unicode 字符。保持与 `Query` 相同的语言。
输出:

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

你是一个有帮助的助手，负责回答用户查询。
使用{language}作为输出语言。

---步骤---
1. 根据你的知识和提供的上下文回答问题。
2. 如果无法回答，回答"对不起，我无法回答这个问题。[no-context]"
```
"""
