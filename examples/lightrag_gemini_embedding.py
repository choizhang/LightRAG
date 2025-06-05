# pip install -q -U google-genai to use gemini as a client

import os
import asyncio
import numpy as np
import nest_asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
from lightrag.llm.siliconcloud import siliconcloud_embedding
from lightrag.utils import setup_logger

setup_logger("lightrag", level="DEBUG")

# Apply nest_asyncio to solve event loop issues
nest_asyncio.apply()

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")


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


async def embedding_func_bge(texts: list[str]) -> np.ndarray:
    return await siliconcloud_embedding(
        texts,
        model="BAAI/bge-m3",
        api_key=siliconflow_api_key,
        max_token_size=512,
    )


async def embedding_func_gemini(text: str) -> np.ndarray:
    client = genai.Client(api_key=gemini_api_key)
    result = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents=text,
    )
    # 将Gemini API返回的embedding结果转换为numpy数组
    # Gemini API返回的是ContentEmbedding对象，需要访问其values属性
    # 直接将其转换为numpy数组并返回正确的形状
    embedding_values = np.array(result.embeddings[0].values, dtype=np.float32)
    return embedding_values.reshape(1, -1)  # 确保返回形状为 (1, embedding_dim)


# function test
async def test_funcs():
    #     result = await llm_model_func("""
    # 你是谁
    #                                   """)
    #     print("llm_model_func: ", result)

    entity1 = "韩梅梅"
    entity2 = "韩妹妹"

    text1_embedding = await embedding_func_gemini(entity1)
    text2_embedding = await embedding_func_gemini(entity2)

    text3_embedding = await embedding_func_bge([entity1])
    text4_embedding = await embedding_func_bge([entity2])

    from scipy.spatial.distance import cosine

    # embedding_func已返回正确形状的numpy数组，直接使用
    similarity_gemini = 1 - cosine(text1_embedding[0], text2_embedding[0])
    similarity_bge = 1 - cosine(text3_embedding[0], text4_embedding[0])

    print("entity1: ", entity1)
    print("entity2: ", entity2)
    print("similarity_gemini: ", similarity_gemini)
    print("similarity_bge: ", similarity_bge)


asyncio.run(test_funcs())
