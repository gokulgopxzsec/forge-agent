import json
import ollama


MODEL = "qwen3:8b"

client = ollama.Client(
    host="http://127.0.0.1:11434"
)


def ask_qwen(prompt: str) -> str:

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def ask_qwen_json(prompt: str) -> dict:

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a business research analyst. "
                    "Return ONLY valid JSON. "
                    "Do not invent facts. "
                    "Use only the evidence provided."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
    )

    content = response["message"]["content"]

    return json.loads(content)