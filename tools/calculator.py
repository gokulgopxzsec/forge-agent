import json


def calculator(expression: str):
    """Safely evaluate a basic mathematical expression."""

    allowed = set("0123456789+-*/(). ")

    if not all(char in allowed for char in expression):
        return {
            "error": "Expression contains unsupported characters."
        }

    try:
        result = eval(expression, {"__builtins__": {}}, {})

        return {
            "expression": expression,
            "result": result
        }

    except Exception as e:
        return {
            "error": str(e),
            "expression": expression
        }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic mathematical calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression such as 25 * 4 / 5"
                }
            },
            "required": ["expression"]
        }
    }
}