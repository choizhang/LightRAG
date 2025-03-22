import json
import os
import tiktoken
from openai import OpenAI


def openai_complete_if_cache(
    model="Qwen/Qwen2.5-7B-Instruct",
    prompt=None,
    system_prompt=None,
    history_messages=[],
    **kwargs,
) -> str:
    openai_client = OpenAI(
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1/",
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    response = openai_client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    return response.choices[0].message.content


ENCODER = None


def get_summary(context, tot_tokens=900):
    global ENCODER
    if ENCODER is None:
        ENCODER = tiktoken.encoding_for_model("gpt-4o")

    tokens = ENCODER.encode(context)
    half_tokens = tot_tokens // 2

    start_tokens = tokens[1000 : 1000 + half_tokens]
    end_tokens = tokens[-(1000 + half_tokens) : 1000]

    summary_tokens = start_tokens + end_tokens
    summary = ENCODER.decode(summary_tokens)

    return summary


clses = ["mix"]
for cls in clses:
    with open(f"./datasets/unique_contexts/{cls}_unique_contexts.json", mode="r") as f:
        unique_contexts = json.load(f)

    summaries = [get_summary(context) for context in unique_contexts]

    total_description = "\n\n".join(summaries)

    prompt = f"""
    Given the following description of a dataset:

    {total_description}

    Please identify 5 potential users who would engage with this dataset. For each user, list 5 tasks they would perform with this dataset. Then, for each (user, task) combination, generate 5 questions that require a high-level understanding of the entire dataset.

    Output the results in the following structure:
    - User 1: [user description]
        - Task 1: [task description]
            - Question 1:
            - Question 2:
            - Question 3:
            - Question 4:
            - Question 5:
        - Task 2: [task description]
            ...
        - Task 5: [task description]
    - User 2: [user description]
        ...
    - User 5: [user description]
        ...
    """

    result = openai_complete_if_cache(prompt=prompt)

    file_path = f"./datasets/questions/{cls}_questions.txt"
    with open(file_path, "w") as file:
        file.write(result)

    print(f"{cls}_questions written to {file_path}")
