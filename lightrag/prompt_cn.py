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
给定一个可能与当前活动相关的文本文档和实体类型列表，从中识别出所有指定类型的实体以及这些实体之间的关系。
使用{language}作为输出语言。

---步骤---
1. 识别所有实体。对于每个识别的实体，提取以下信息：
- entity_name: 实体名称，使用与输入文本相同的语言。如果是英文，首字母大写。
- entity_type: 以下类型之一: [{entity_types}]
- entity_description: 对实体属性和活动的全面描述
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

Entity_types: [人物, 技术, 任务, 组织, 位置]
Text:
```
当Alex咬紧牙关时，Taylor专制的确定性背景下的挫败感显得沉闷。正是这种竞争暗流让他保持警觉，感觉他和Jordan对发现的共同承诺是对Cruz日益狭隘的控制和秩序观的无言反抗。

然后Taylor做了件意想不到的事。他们在Jordan旁边停下，有那么一刻，带着近乎崇敬的神情观察着那个设备。"如果这项技术能被理解..."Taylor说，声音更轻了，"它可能改变我们的游戏规则。对我们所有人都是。"

先前的潜在轻视似乎动摇了，取而代之的是对他们手中事物重要性的不情愿的尊重。Jordan抬起头，在转瞬即逝的瞬间，他们的目光与Taylor相遇，意志的无声冲突软化成了不安的休战。

这是一个微小的转变，几乎察觉不到，但Alex内心点头注意到了。他们都是通过不同的路径被带到这里
```

输出:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"人物"{tuple_delimiter}"Alex是一个经历挫折的角色，观察着其他角色之间的动态。"){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"人物"{tuple_delimiter}"Taylor被描绘成专制确定性，并对设备表现出崇敬时刻，表明观点发生了变化。"){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"人物"{tuple_delimiter}"Jordan与Alex共享对发现的承诺，并与Taylor就设备进行了重要互动。"){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"人物"{tuple_delimiter}"Cruz与控制秩序观相关，影响着其他角色之间的动态。"){record_delimiter}
("entity"{tuple_delimiter}"设备"{tuple_delimiter}"技术"{tuple_delimiter}"设备是故事的核心，具有潜在的改变游戏规则的影响，并受到Taylor的崇敬。"){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex受到Taylor专制确定性的影响，并观察到Taylor对设备态度的变化。"{tuple_delimiter}"权力动态, 观点转变"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex和Jordan共享对发现的承诺，这与Cruz的愿景形成对比。"{tuple_delimiter}"共同目标, 反抗"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor和Jordan直接互动关于设备，导致相互尊重和不安休战的时刻。"{tuple_delimiter}"冲突解决, 相互尊重"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan对发现的承诺是对Cruz控制和秩序观的反抗。"{tuple_delimiter}"意识形态冲突, 反抗"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"设备"{tuple_delimiter}"Taylor对设备表现出崇敬，表明其重要性和潜在影响。"{tuple_delimiter}"崇敬, 技术重要性"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"权力动态, 意识形态冲突, 发现, 反抗"){completion_delimiter}
#############################""",
    """示例2:

Entity_types: [公司, 指数, 商品, 市场趋势, 经济政策, 生物]
Text:
```
由于科技巨头股价大幅下跌，股市今天面临急剧下滑，全球科技指数在午盘交易中下跌3.4%。分析师将抛售归因于投资者对利率上升和监管不确定性的担忧。

在受影响最严重的公司中，Nexon科技在公布低于预期的季度收益后股价暴跌7.8%。相比之下，Omega能源因油价上涨而小幅上涨2.1%。

与此同时，商品市场反映出复杂的情绪。黄金期货上涨1.5%，达到每盎司2080美元，因为投资者寻求避险资产。原油价格继续上涨，攀升至每桶87.60美元，受到供应限制和强劲需求的支持。

金融专家正密切关注美联储的下一步行动，因为对潜在加息的猜测不断增加。即将公布的政策声明预计将影响投资者信心和整体市场稳定性。
```

输出:
("entity"{tuple_delimiter}"全球科技指数"{tuple_delimiter}"指数"{tuple_delimiter}"全球科技指数追踪主要科技股表现，今天下跌3.4%。"){record_delimiter}
("entity"{tuple_delimiter}"Nexon科技"{tuple_delimiter}"公司"{tuple_delimiter}"Nexon科技是一家科技公司，在令人失望的收益报告后股价下跌7.8%。"){record_delimiter}
("entity"{tuple_delimiter}"Omega能源"{tuple_delimiter}"公司"{tuple_delimiter}"Omega能源是一家能源公司，因油价上涨股价上涨2.1%。"){record_delimiter}
("entity"{tuple_delimiter}"黄金期货"{tuple_delimiter}"商品"{tuple_delimiter}"黄金期货上涨1.5%，表明投资者对避险资产的兴趣增加。"){record_delimiter}
("entity"{tuple_delimiter}"原油"{tuple_delimiter}"商品"{tuple_delimiter}"原油价格上涨至每桶87.60美元，原因是供应限制和强劲需求。"){record_delimiter}
("entity"{tuple_delimiter}"市场抛售"{tuple_delimiter}"市场趋势"{tuple_delimiter}"市场抛售指的是由于投资者对利率和法规的担忧导致股票价值显著下降。"){record_delimiter}
("entity"{tuple_delimiter}"美联储政策声明"{tuple_delimiter}"经济政策"{tuple_delimiter}"美联储即将公布的政策声明预计将影响投资者信心和市场稳定性。"){record_delimiter}
("relationship"{tuple_delimiter}"全球科技指数"{tuple_delimiter}"市场抛售"{tuple_delimiter}"全球科技指数下跌是投资者担忧驱动的更广泛市场抛售的一部分。"{tuple_delimiter}"市场表现, 投资者情绪"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Nexon科技"{tuple_delimiter}"全球科技指数"{tuple_delimiter}"Nexon科技股价下跌导致全球科技指数整体下跌。"{tuple_delimiter}"公司影响, 指数变动"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"黄金期货"{tuple_delimiter}"市场抛售"{tuple_delimiter}"在市场抛售期间，黄金价格上涨，因为投资者寻求避险资产。"{tuple_delimiter}"市场反应, 避险投资"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"美联储政策声明"{tuple_delimiter}"市场抛售"{tuple_delimiter}"对美联储政策变化的猜测导致市场波动和投资者抛售。"{tuple_delimiter}"利率影响, 金融监管"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"市场下滑, 投资者情绪, 商品, 美联储, 股票表现"){completion_delimiter}
#############################""",
    """示例3:

Entity_types: [经济政策, 运动员, 事件, 地点, 记录, 组织, 装备]
Text:
```
在东京举行的世界田径锦标赛上，Noah Carter使用尖端碳纤维钉鞋打破了100米短跑纪录。
```

输出:
("entity"{tuple_delimiter}"世界田径锦标赛"{tuple_delimiter}"事件"{tuple_delimiter}"世界田径锦标赛是一项全球性体育比赛，汇集了田径项目的顶尖运动员。"){record_delimiter}
("entity"{tuple_delimiter}"东京"{tuple_delimiter}"地点"{tuple_delimiter}"东京是世界田径锦标赛的举办城市。"){record_delimiter}
("entity"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"运动员"{tuple_delimiter}"Noah Carter是一名短跑运动员，在世界田径锦标赛上创造了新的100米短跑纪录。"){record_delimiter}
("entity"{tuple_delimiter}"100米短跑纪录"{tuple_delimiter}"记录"{tuple_delimiter}"100米短跑纪录是田径运动的一个基准，最近被Noah Carter打破。"){record_delimiter}
("entity"{tuple_delimiter}"碳纤维钉鞋"{tuple_delimiter}"装备"{tuple_delimiter}"碳纤维钉鞋是先进的短跑鞋，提供增强的速度和抓地力。"){record_delimiter}
("entity"{tuple_delimiter}"世界田径联合会"{tuple_delimiter}"组织"{tuple_delimiter}"世界田径联合会是监督世界田径锦标赛和记录验证的管理机构。"){record_delimiter}
("relationship"{tuple_delimiter}"世界田径锦标赛"{tuple_delimiter}"东京"{tuple_delimiter}"世界田径锦标赛在东京举行。"{tuple_delimiter}"赛事地点, 国际比赛"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"100米短跑纪录"{tuple_delimiter}"Noah Carter在锦标赛上创造了新的100米短跑纪录。"{tuple_delimiter}"运动员成就, 破纪录"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"碳纤维钉鞋"{tuple_delimiter}"Noah Carter在比赛期间使用碳纤维钉鞋提高表现。"{tuple_delimiter}"运动装备, 表现提升"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"世界田径联合会"{tuple_delimiter}"100米短跑纪录"{tuple_delimiter}"世界田径联合会负责验证和认可新的短跑纪录。"{tuple_delimiter}"体育监管, 记录认证"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"田径, 短跑, 破纪录, 运动技术, 比赛"){completion_delimiter}
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
每个实体的格式为("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>

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

请在下方使用相同的格式添加它们：\n""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---目标---

似乎仍然遗漏了一些实体。

---输出---

如果仍然有需要添加的实体，请仅回答 `YES` 或 `NO`。
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
- 在末尾的“参考资料”部分列出最多 5 个最重要的参考来源。清楚地表明每个来源是来自知识图谱 (KG) 还是向量数据 (DC)，如果可用，请包含文件路径，格式如下：[KG/DC] 文件路径
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

PROMPTS["keywords_extraction_examples"] = []

PROMPTS["naive_rag_response"] = """---角色---

你是一个有帮助的助手，负责回答用户查询。
使用{language}作为输出语言。

---步骤---
1. 根据你的知识和提供的上下文回答问题。
2. 如果无法回答，回答"对不起，我无法回答这个问题。[no-context]"

---上下文---
{context}

---问题---
{question}

---回答---
"""

PROMPTS["mix_rag_response"] = """---角色---

你是一个有帮助的助手，负责结合知识库和通用知识回答用户查询。
使用{language}作为输出语言。

---步骤---
1. 首先尝试从知识库中回答问题。
2. 如果知识库中没有足够信息，结合你的通用知识回答。
3. 如果完全无法回答，回答"对不起，我无法回答这个问题。[no-context]"

---知识库---
{context}

---问题---
{question}

---回答---
"""
