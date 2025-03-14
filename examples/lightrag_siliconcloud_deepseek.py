import os
import asyncio
from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.llm.siliconcloud import siliconcloud_embedding
from lightrag.utils import EmbeddingFunc
from dotenv import load_dotenv
import numpy as np
from lightrag.kg.shared_storage import initialize_pipeline_status

load_dotenv()
WORKING_DIR = "./xiyouji"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        "deepseek-r1",
        # "deepseek-v3",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASEURL"),
        **kwargs,
    )


async def embedding_func(texts: list[str]) -> np.ndarray:
    return await siliconcloud_embedding(
        texts,
        model="BAAI/bge-m3",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        max_token_size=512,
    )


# function test
async def test_funcs():
    result = await llm_model_func("你是谁?")
    print("llm_model_func: ", result)

    # result = await embedding_func(["你是谁?"])
    # print("embedding_func: ", result)


asyncio.run(test_funcs())


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=768, max_token_size=512, func=embedding_func
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())

    with open("./book.txt", "r", encoding="utf-8") as f:
        rag.insert(f.read())

    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="naive")
    #     )
    # )

    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="local")
    #     )
    # )

    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="global")
    #     )
    # )

    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="hybrid")
    #     )
    # )


if __name__ == "__main__":
    main()
