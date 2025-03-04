import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.llm.siliconcloud import siliconcloud_embedding
from lightrag.utils import EmbeddingFunc
import numpy as np
from lightrag.kg.shared_storage import initialize_pipeline_status

siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_baseurl = os.getenv("DEEPSEEK_BASEURL")

WORKING_DIR = "./lilei"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        "Qwen/Qwen2.5-7B-Instruct",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=siliconflow_api_key,
        base_url="https://api.siliconflow.cn/v1",
        **kwargs,
    )

# async def llm_model_func(
#     prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
# ) -> str:
#     return await openai_complete_if_cache(
#         "deepseek-r1",
#         prompt,
#         system_prompt=system_prompt,
#         history_messages=history_messages,
#         api_key=deepseek_api_key,
#         base_url=deepseek_baseurl,
#         **kwargs,
#     )

# qwen的response不是标准的openai数据格式，需要自己单独处理
# async def llm_model_func(
#     prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
# ) -> str:
#     return await openai_complete_if_cache(
#         "qwen72b-hongkong",
#         prompt,
#         system_prompt=system_prompt,
#         history_messages=history_messages,
#         api_key=deepseek_api_key,
#         base_url=deepseek_baseurl,
#         **kwargs,
#     )


async def embedding_func(texts: list[str]) -> np.ndarray:
    return await siliconcloud_embedding(
        texts,
        model="BAAI/bge-m3",
        api_key=siliconflow_api_key,
        max_token_size=512,
    )


# function test
async def test_funcs():
    result = await llm_model_func("成都今天天气如何?")
    print("llm_model_func: ", result)

    result = await embedding_func(["How are you?"])
    print("embedding_func: ", result)

async def get_embedding_dim():
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    embedding_dim = embedding.shape[1]
    return embedding_dim


asyncio.run(test_funcs())

# asyncio.run(embedding_dimension = get_embedding_dim())

# print("embedding_dimension: ", embedding_dimension)

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024, max_token_size=512, func=embedding_func
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

question = "孙悟空的师傅是谁?"
# question = "孙悟空有几个师傅，分别是谁?"

def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())

    with open("./ragtest/lilei/lilei_1.txt", "r", encoding="utf-8") as f:
        rag.insert(f.read())

    # 读取目录
    # contents = []
    # current_dir = Path(__file__).parent
    # # 指定文件目录
    # files_dir = current_dir / "files/inputs"
    # for file_path in files_dir.glob("*.txt"):
    #     with open(file_path, "r", encoding="utf-8") as file:
    #         content = file.read()
    #     contents.append(content)
    # rag.insert(contents)



    # print(
    #     rag.query(question, param=QueryParam(mode="naive"))
    # )

    # print(
    #     rag.query(question, param=QueryParam(mode="local"))
    # )

    # print(
    #     rag.query(question, param=QueryParam(mode="global"))
    # )

    # print(
    #     rag.query(question, param=QueryParam(mode="hybrid"))
    # )


if __name__ == "__main__":
    main()