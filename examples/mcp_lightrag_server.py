# 请确保在运行此脚本前已安装必要的库: fastapi, uvicorn, google-genai, python-dotenv, lightrag, numpy, sentence-transformers (或您选择的 embedding 提供者)
# pip install fastapi uvicorn google-genai python-dotenv lightrag numpy sentence-transformers
#
# 并且已设置必要的环境变量, 例如 GEMINI_API_KEY 和 SILICONFLOW_API_KEY (如果使用 lightrag_gemini.py 中的默认函数)
#
# 运行服务器前, 请激活您的 conda 环境:
# cd /Users/choizhang/LightRAG
# conda activate lightrag
#
# 然后运行脚本:
# python /Users/choizhang/LightRAG/examples/mcp_lightrag_server.py

import os
import numpy as np
import nest_asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

# 尝试导入 google-genai, 如果失败则提示用户安装
try:
    from google import genai
    from google.genai import types
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

# 应用 nest_asyncio 来解决 FastAPI/Uvicorn 与 asyncio 事件循环的潜在冲突
nest_asyncio.apply()

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


# 定义 LLM 模型函数 (改编自 lightrag_gemini.py)
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
            generation_config=types.GenerationConfig(
                max_output_tokens=5000, temperature=0, top_k=10
            ),
        )
        return response.text
    except Exception as e:
        print(f"调用 Gemini 模型失败: {e}")
        raise


# 定义 Embedding 函数 (改编自 lightrag_gemini.py)
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
        raise  # 重新抛出异常，以便 FastAPI 启动时能捕获到


# FastAPI 应用实例
app = FastAPI(
    title="LightRAG MCP Server",
    description="一个通过 FastAPI 实现的 MCP 服务器，用于 LightRAG 的不同搜索模式。",
    version="0.1.0",
)


# 请求体模型
class QueryRequest(BaseModel):
    query_text: str


@app.on_event("startup")
async def startup_event():
    """FastAPI 应用启动时执行的事件，用于初始化 RAG 实例"""
    await initialize_rag_instance()
    abc = await perform_query("李进是谁", "naive")
    print(abc)
    if rag_instance is None:
        # 如果 RAG 初始化失败，可以阻止服务器启动或记录严重错误
        print("错误：RAG 实例未能初始化。服务器可能无法正常工作。")
        # raise RuntimeError("RAG instance could not be initialized.") # 取消注释以在初始化失败时停止服务器


async def perform_query(query_text: str, mode: str):
    """执行 RAG 查询的辅助函数"""
    if rag_instance is None:
        raise HTTPException(
            status_code=503, detail="RAG 服务当前不可用，正在初始化或初始化失败。"
        )
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
        raise HTTPException(status_code=500, detail=f"查询处理时发生错误: {str(e)}")


@app.post("/mcp/naive_search")
async def naive_search(request: QueryRequest):
    """执行 Naive Search"""
    return await perform_query(request.query_text, "naive")


@app.post("/mcp/local_search")
async def local_search(request: QueryRequest):
    """执行 Local Search"""
    return await perform_query(request.query_text, "local")


@app.post("/mcp/global_search")
async def global_search(request: QueryRequest):
    """执行 Global Search"""
    return await perform_query(request.query_text, "global")


@app.post("/mcp/hybrid_search")
async def hybrid_search(request: QueryRequest):
    """执行 Hybrid Search"""
    return await perform_query(request.query_text, "hybrid")


@app.get("/mcp/tools")
async def get_mcp_tools():
    """返回 MCP 服务器提供的工具列表"""
    return [
        {
            "name": "naive_search",
            "description": "执行 Naive Search",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query_text": {"type": "string", "description": "要搜索的文本"}
                },
                "required": ["query_text"],
            },
        },
        {
            "name": "local_search",
            "description": "执行 Local Search",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query_text": {"type": "string", "description": "要搜索的文本"}
                },
                "required": ["query_text"],
            },
        },
        {
            "name": "global_search",
            "description": "执行 Global Search",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query_text": {"type": "string", "description": "要搜索的文本"}
                },
                "required": ["query_text"],
            },
        },
        {
            "name": "hybrid_search",
            "description": "执行 Hybrid Search",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query_text": {"type": "string", "description": "要搜索的文本"}
                },
                "required": ["query_text"],
            },
        },
    ]


# 主程序入口，用于启动 Uvicorn 服务器
if __name__ == "__main__":
    print("启动 FastAPI 服务器，监听地址 http://127.0.0.1:8006")
    print(f"LightRAG 工作目录: {WORKING_DIR}")
    print("请确保已激活 conda 环境 'lightrag' 并已安装所有依赖。")
    print("API 端点:")
    print("  - POST /mcp/naive_search")
    print("  - POST /mcp/local_search")
    print("  - POST /mcp/global_search")
    print("  - POST /mcp/hybrid_search")
    print("  - GET /mcp/tools")  # 添加新的端点提示
    example_request_body = {"query_text": "your query here"}
    print(f"请求体示例: {example_request_body}")

    # 运行 Uvicorn 服务器
    # host="0.0.0.0" 使其可以从网络访问，如果只需要本地访问，可以使用 "127.0.0.1"
    # reload=True 用于开发时自动重载，生产环境应移除
    uvicorn.run(app, host="127.0.0.1", port=8006, log_level="info")
