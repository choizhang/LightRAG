# pip install -q -U google-genai to use gemini as a client

import os
import asyncio
import numpy as np
import nest_asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
from lightrag.utils import EmbeddingFunc
from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.siliconcloud import siliconcloud_embedding
from lightrag.utils import setup_logger

setup_logger("lightrag", level="DEBUG")

# Apply nest_asyncio to solve event loop issues
nest_asyncio.apply()

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")

WORKING_DIR = "./lilei"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    # 1. Initialize the GenAI Client with your Gemini API Key
    client = genai.Client(api_key=gemini_api_key)

    # 2. Combine prompts: system prompt, history, and user prompt
    if history_messages is None:
        history_messages = []

    combined_prompt = ""
    if system_prompt:
        combined_prompt += f"{system_prompt}\n"

    for msg in history_messages:
        # Each msg is expected to be a dict: {"role": "...", "content": "..."}
        combined_prompt += f"{msg['role']}: {msg['content']}\n"

    # Finally, add the new user prompt
    combined_prompt += f"user: {prompt}"

    # 3. Call the Gemini model
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[combined_prompt],
        config=types.GenerateContentConfig(
            max_output_tokens=5000, temperature=0, top_k=10
        ),
    )

    # 4. Return the response text
    return response.text


async def embedding_func(texts: list[str]) -> np.ndarray:
    return await siliconcloud_embedding(
        texts,
        model="BAAI/bge-m3",
        api_key=siliconflow_api_key,
        max_token_size=512,
    )


# function test
async def test_funcs():
    result = await llm_model_func("""
李进的爸爸是李雷，李进的妈妈是韩梅梅，李雷跟韩梅梅是夫妻，李进的爷爷是李双喜

：将下面的聊天对话中的指示代词（你、我、他/她、你们、我们、他们等）、亲戚关系昵称根据上面的信息替换为具体的人名返回，无法替换为具体人名的亲戚关系昵称按照下面近义词列表进行规范化为冒号左边的称谓
近义词列表
父亲：爸爸、爹、老爸,
母亲：妈妈、妈、娘、老妈、妈咪、阿妈,
祖父：爷爷、爷、阿爷、老爷,
祖母：奶奶、奶、阿奶、老奶,
外祖父：外公、姥爷、公公,
外祖母：外婆、姥姥、婆婆,
丈夫：老公、先生、那口子、孩儿他爹、当家的、老伴、夫君,
妻子：老婆、太太、那口子、孩儿他妈、当家的、老伴、夫人,
儿媳妇：儿媳,
女婿：小女婿,
儿子：儿、娃、小子,
女儿：妮儿、丫头、闺女,
哥哥：哥哥、哥、大哥、阿哥,
姐姐：姐姐、姐、大姐、阿姐,
弟弟：弟弟、弟、小弟、老弟,
妹妹：妹妹、妹、小妹、老妹,

韩梅梅: 今天你爷爷去医院体检，医生说他得了糖尿病，以后要多注意饮食，控制血糖。
李进: 糖尿病是什么，是不是尿里面有糖？奶奶是不是很担心？
韩梅梅: 结果是这样，主要还是身体里面的胰岛素分泌不够。你爸去哪了？
李进: 不知道，估计在我奶奶家。我小妹去上学了吗？
韩梅梅: 不知道，我们一起去找他们吧
                                  """)
    print("llm_model_func: ", result)


# asyncio.run(test_funcs())


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        entity_extract_max_gleaning=1,
        enable_llm_cache=True,
        enable_llm_cache_for_entity_extract=True,
        embedding_cache_config={"enabled": True, "similarity_threshold": 0.90},
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=8192,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    # 测试删除文档
    # await rag.adelete_by_doc_id("doc-4a25eb96a1dcad04847356329f7806ac")

    return rag


def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())

    _custom_kg = {
        "chunks": [
            {"content": "李双喜: 我是李进的爷爷，我喜欢打羽毛球", "source_id": "doc-1"}
        ],
        "entities": [
            {
                "entity_name": "李双喜",
                "entity_type": "人物",
                "description": "李进的爷爷",
                "source_id": "doc-1",
            },
            {
                "entity_name": "羽毛球",
                "entity_type": "运动",
                "description": "李双喜欢打羽毛球",
                "source_id": "doc-1",
            },
        ],
        "relationships": [
            {
                "src_id": "李双喜",
                "tgt_id": "李进",
                "description": "李进的爷爷",
                "keywords": "亲属关系",
                "weight": 1.0,
                "source_id": "doc-1",
            },
            {
                "src_id": "李双喜",
                "tgt_id": "羽毛球",
                "description": "李双喜喜欢打羽毛球",
                "keywords": "爱好",
                "weight": 1.0,
                "source_id": "doc-1",
            },
        ],
    }
    # rag.insert_custom_kg(custom_kg)

    # with open("./ragtest/lilei/lilei_1.txt", "r") as f:
    #     rag.insert(f.read())

    # with open("./ragtest/cd/111.pdf", "r") as f:
    #     rag.insert(f.read())

    import textract

    file_path = "./ragtest/cd/111.pdf"
    text_content = textract.process(file_path)

    rag.insert(text_content.decode("utf-8"))

    # 添加关系推理
    # asyncio.run(rag.infer_new_relationships())

    _question = """
总结一下整个知识图谱中人物之间的亲属关系。比如A是B的爸爸，C是B的妈妈，A和C是夫妻。
    """
    # print(
    #     rag.query(_question, param=QueryParam(mode="naive"))
    # )

    # print(
    #     rag.query(_question, param=QueryParam(mode="local"))
    # )

    # print(
    #     rag.query(_question, param=QueryParam(mode="global"))
    # )

    # print(
    #     rag.query(
    #         _question,
    #         param=QueryParam(
    #             mode="hybrid", only_need_context=False, only_need_prompt=False, top_k=60
    #         ),
    #     )
    # )


if __name__ == "__main__":
    main()
