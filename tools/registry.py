from tools.calculator import calculator
from tools.web import fetch_url
from tools.search import web_search


TOOLS = {
    "calculator": calculator,
    "fetch_url": fetch_url,
    "web_search": web_search,
}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression."
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch a webpage and extract its readable text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The complete URL to fetch."
                    }
                },
                "required": ["url"]
            }
        }
    },{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for information. "
            "Use this to discover relevant websites "
            "and information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The web search query."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return."
                }
            },
            "required": ["query"]
        }
    }
}
]


def execute_tool(name, arguments):
    """Execute a registered tool."""

    if name not in TOOLS:
        return {
            "error": f"Unknown tool: {name}"
        }

    try:
        return TOOLS[name](**arguments)

    except Exception as e:
        return {
            "error": str(e)
        }