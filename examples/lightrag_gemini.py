# pip install -q -U google-genai to use gemini as a client

import os
import asyncio
import numpy as np
import nest_asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
from lightrag.utils import EmbeddingFunc
from lightrag import LightRAG, QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.siliconcloud import siliconcloud_embedding

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
        config=types.GenerateContentConfig(max_output_tokens=5000, temperature=0, top_k=10),
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

                                  """)
    print("llm_model_func: ", result)


# asyncio.run(test_funcs())

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        entity_extract_max_gleaning=0,
        enable_llm_cache=True,
        enable_llm_cache_for_entity_extract=True,
        embedding_cache_config={"enabled": True,"similarity_threshold": 0.90},
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=8192,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())
    with open("./ragtest/lilei/lilei_1.txt", "r") as f:
        rag.insert(f.read())

    question = '''
    李进家的物业费是多少钱
    '''
    # print(
    #     rag.query(question, param=QueryParam(mode="naive"))
    # )

    # print(
    #     rag.query(question, param=QueryParam(mode="local"))
    # )

    # print(
    #     rag.query(question, param=QueryParam(mode="hybrid", only_need_context=False, only_need_prompt=False, top_k=10))
    # )

    # print(
    #     rag.query(question, param=QueryParam(mode="hybrid"))
    # )

if __name__ == "__main__":
    main()