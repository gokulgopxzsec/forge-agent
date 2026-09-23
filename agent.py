import json
import ollama

from tools.registry import TOOL_DEFINITIONS, execute_tool


MODEL = "qwen3:8b"

client = ollama.Client(
    host="http://127.0.0.1:11434"
)


SYSTEM_PROMPT = """
You are Forge Agent, a local AI agent running on the user's computer.

You have access to tools.

When a tool is useful, call the appropriate tool.
After receiving a tool result, analyze it and decide whether another
tool is needed.

Do not invent tool results.

When the task is complete, provide a concise final answer.
"""


def run_agent(user_message):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    max_iterations = 8

    for iteration in range(1, max_iterations + 1):

        print()
        print(f"🧠 AGENT ITERATION {iteration}")
        print()

        response = client.chat(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS
        )

        assistant_message = response["message"]

        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])

        # No tool call means the agent has finished.
        if not tool_calls:

            print("=" * 60)
            print("✅ FINAL ANSWER")
            print("=" * 60)

            print(assistant_message.get("content", ""))

            return

        # Execute requested tools.
        for tool_call in tool_calls:

            function = tool_call["function"]

            tool_name = function["name"]
            arguments = function.get("arguments", {})

            print("=" * 60)
            print(f"🔧 TOOL: {tool_name}")
            print(f"📥 ARGUMENTS: {arguments}")
            print("=" * 60)

            result = execute_tool(
                tool_name,
                arguments
            )

            print("📤 RESULT:")
            print(json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            ))

            # Give the tool result back to the model.
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                }
            )

    print("⚠️ Maximum agent iterations reached.")


def main():

    print("=" * 60)
    print("FORGE AGENT v0.2")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print()
    print("Type 'exit' to quit.")
    print()

    while True:

        try:
            user_input = input("You > ").strip()

        except KeyboardInterrupt:
            print("\nExiting.")
            break

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit"
        }:
            break

        run_agent(user_input)


if __name__ == "__main__":
    main()