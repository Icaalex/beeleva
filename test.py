import os
from openai import OpenAI

client =  OpenAI(
        api_key="sk-ws-H.PXYHLH.2ziL.MEQCIDXTMUOWvLEmATlSHKQJxv6ZetLyVsuBbGQ-3Cwp7DfAAiBVjwEJfnuTgTRnnGMnU9U4Ixt0tPLM36ZqR41v5u2V7Q",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )

completion = client.chat.completions.create(
    model = "qwen3.7-plus",
    messages = [{"role": "user", "content": "say: Beeleva is online." }]
)

print(completion.choices[0].message.content)