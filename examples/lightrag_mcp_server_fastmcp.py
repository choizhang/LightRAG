#!/usr/bin/env python
import os
import asyncio
import numpy as np
from dotenv import load_dotenv
from google import genai
from lightrag.llm.siliconcloud import siliconcloud_embedding

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

# Import MCP server SDK components
from mcp.server.fastmcp import FastMCP

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取 API 密钥
gemini_api_key = os.getenv("GEMINI_API_KEY")
siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")

# 设置已经构建好的知识图谱工作目录
WORKING_DIR = "/Users/choizhang/LightRAG/lilei"


# 定义 LLM 模型函数
async def llm_model_func(
    prompt: str, system_prompt: str = None, history_messages: list = None, **kwargs
) -> str:
    """调用 Gemini 模型生成文本的异步函数"""
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY 未设置，无法调用 LLM。")
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        raise ConnectionError(f"初始化 Gemini 客户端失败: {e}")

    if history_messages is None:
        history_messages = []

    combined_prompt_parts = []
    if system_prompt:
        combined_prompt_parts.append(system_prompt)

    for msg in history_messages:
        combined_prompt_parts.append(f"{msg['role']}: {msg['content']}")

    combined_prompt_parts.append(f"user: {prompt}")
    final_prompt_content = "\n".join(combined_prompt_parts)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[final_prompt_content],
        )
        return response.text
    except Exception as e:
        print(f"调用 Gemini 模型失败: {e}")
        raise


# 定义 Embedding 函数
async def embedding_func(texts: list[str]) -> np.ndarray:
    """使用 SiliconFlow 服务为文本列表生成嵌入向量的异步函数"""
    if not siliconflow_api_key:
        raise ValueError("SILICONFLOW_API_KEY 未设置，无法生成 embeddings。")
    try:
        return await siliconcloud_embedding(
            texts,
            model="BAAI/bge-m3",
            api_key=siliconflow_api_key,
            max_token_size=512,
        )
    except Exception as e:
        print(f"调用 SiliconFlow embedding 服务失败: {e}")
        raise


# 全局 RAG 实例变量
rag_instance: LightRAG = None


async def initialize_rag_instance():
    """初始化 LightRAG 实例并存储在全局变量中"""
    global rag_instance
    try:
        rag_instance = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,
                max_token_size=8192,
                func=embedding_func,
            ),
            enable_llm_cache=True,
            embedding_cache_config={"enabled": True, "similarity_threshold": 0.95},
        )
        await rag_instance.initialize_storages()
        await initialize_pipeline_status()
        print("LightRAG 实例初始化完成。")
    except Exception as e:
        print(f"LightRAG 实例初始化失败: {e}")
        rag_instance = None
        raise


async def perform_query(query_text: str, mode: str):
    """执行 RAG 查询的辅助函数"""
    try:
        query_param = QueryParam(
            mode=mode,
            only_need_context=False,
            only_need_prompt=False,
            top_k=60 if mode == "hybrid" else 5,
        )

        response = await rag_instance.aquery(query_text, param=query_param)
        return {"query_text": query_text, "mode": mode, "result": response}
    except Exception as e:
        print(f"查询处理失败 (模式: {mode}): {e}")
        raise


mcp = FastMCP("lightrag-mcp")


@mcp.tool("naive_search")
async def naive_search(query_text: str) -> dict:
    """执行 Naive Search"""
    return await perform_query(query_text, "naive")


@mcp.tool("local_search")
async def local_search(query_text: str) -> dict:
    """执行 Local Search"""
    return await perform_query(query_text, "local")


@mcp.tool("global_search")
async def global_search(query_text: str) -> dict:
    """执行 Global Search"""
    return await perform_query(query_text, "global")


@mcp.tool("hybrid_search")
async def hybrid_search(query_text: str) -> dict:
    """执行 Hybrid Search"""
    return await perform_query(query_text, "hybrid")


async def main():
    try:
        await initialize_rag_instance()
    except Exception as e:
        print(f"初始化 RAG 实例失败: {e}")

    # 启动服务器
    print("LightRAG MCP 服务器正在启动...")
    await mcp.run_stdio_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
