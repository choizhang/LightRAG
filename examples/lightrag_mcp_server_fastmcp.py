#!/usr/bin/env python
import os
import asyncio
import numpy as np
from dotenv import load_dotenv

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

# Import MCP server SDK components
from mcp.server.fastmcp import FastMCP
# from modelcontextprotocol.types import McpError, ErrorCode

# 尝试导入 google-genai, 如果失败则提示用户安装
try:
    from google import genai
except ImportError:
    print(
        "google-genai library not found. Please install it using: pip install google-genai"
    )
    # 可以选择退出或使用备用 LLM
    # exit(1)

# 尝试导入 siliconcloud_embedding, 如果失败则提示用户检查 lightrag.llm.siliconcloud
try:
    from lightrag.llm.siliconcloud import siliconcloud_embedding
except ImportError:
    print(
        "siliconcloud_embedding not found. Please ensure lightrag.llm.siliconcloud is correctly set up."
    )
    # 可以选择退出或使用备用 embedding
    # exit(1)

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取 API 密钥
gemini_api_key = os.getenv("GEMINI_API_KEY")
siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")

# 检查 API 密钥是否存在
if not gemini_api_key:
    print("警告: GEMINI_API_KEY 环境变量未设置。LLM 功能可能无法正常工作。")
if not siliconflow_api_key:
    print("警告: SILICONFLOW_API_KEY 环境变量未设置。Embedding 功能可能无法正常工作。")

# 设置 LightRAG 的工作目录
WORKING_DIR = "/Users/choizhang/LightRAG/lilei"  # 用户指定的路径

# 确保工作目录存在
if not os.path.exists(WORKING_DIR):
    try:
        os.makedirs(WORKING_DIR)
        print(f"工作目录 {WORKING_DIR} 已创建.")
    except OSError as e:
        print(f"创建工作目录 {WORKING_DIR} 失败: {e}")
        # 根据需要处理错误，例如退出程序
        # exit(1)


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
            model="gemini-2.0-flash",  # 或者其他合适的模型
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
            model="BAAI/bge-m3",  # 或者其他合适的模型
            api_key=siliconflow_api_key,
            max_token_size=512,  # 根据模型调整
        )
    except Exception as e:
        print(f"调用 SiliconFlow embedding 服务失败: {e}")
        raise


# 全局 RAG 实例变量
rag_instance: LightRAG = None


async def initialize_rag_instance():
    """初始化 LightRAG 实例并存储在全局变量中"""
    global rag_instance
    print("正在初始化 LightRAG 实例...")
    try:
        rag_instance = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,  # BAAI/bge-m3 的维度
                max_token_size=8192,  # 根据 embedding 模型调整
                func=embedding_func,
            ),
            # 根据需要配置其他参数
            enable_llm_cache=True,
            embedding_cache_config={"enabled": True, "similarity_threshold": 0.95},
        )
        await rag_instance.initialize_storages()
        await initialize_pipeline_status()  # 确保 pipeline 状态已初始化
        print("LightRAG 实例初始化完成。")
    except Exception as e:
        print(f"LightRAG 实例初始化失败: {e}")
        rag_instance = None  # 确保在失败时 rag_instance 为 None
        raise  # 重新抛出异常


async def perform_query(query_text: str, mode: str):
    """执行 RAG 查询的辅助函数"""
    if rag_instance is None:
        # Attempt to re-initialize if it failed previously
        try:
            await initialize_rag_instance()
        except Exception:
            pass  # Ignore re-initialization errors here, will be handled below

    try:
        print(f"接收到查询: '{query_text}'，模式: {mode}")
        query_param = QueryParam(
            mode=mode,
            only_need_context=False,
            only_need_prompt=False,
            top_k=60 if mode == "hybrid" else 5,
        )

        response = await rag_instance.aquery(query_text, param=query_param)
        print(f"查询模式 '{mode}' 的响应: {response}")
        return {"query_text": query_text, "mode": mode, "result": response}
    except Exception as e:
        print(f"查询处理失败 (模式: {mode}): {e}")
        # raise McpError(ErrorCode.InternalError, f"查询处理时发生错误: {str(e)}")


# 创建 FastMCP 服务器实例
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


# 错误处理
# @mcp.error_handler
# def handle_error(error):
#     print(f'[MCP Error] {error}', file=sys.stderr)


# 主函数
async def main():
    # 初始化 RAG 实例
    try:
        await initialize_rag_instance()
        abc = await perform_query("李进是谁", "naive")
        print(abc)
    except Exception as e:
        print(f"初始化 RAG 实例失败: {e}")
        # 服务器仍会启动，但工具调用在 RAG 就绪前会失败

    # 启动服务器
    print("LightRAG MCP 服务器正在启动...")
    await mcp.run_stdio_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
