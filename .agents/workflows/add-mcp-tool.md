---
description: Creates a new MCP tool for Karoo chatbot. Generates tool file, registers in MCP server, adds agent trace logging. Asks tool name and purpose first.
---

Create a new MCP tool for the Karoo chatbot system.

Ask me these questions first:
1. What is the tool name? (snake_case, e.g. search_providers)
2. What does this tool do? (plain English description)
3. What inputs does it need? (list the parameters)
4. What should it return?
5. Which Supabase table or external API does it use?

After I answer, create the following:

TOOL FILE (backend/mcp/tools/{tool_name}.py):

Structure must follow this exact pattern:
from db.supabase_client import supabase
from typing import Any

TOOL_DEFINITION = {
    "name": "tool_name",
    "description": "Clear description of what this tool does and WHEN the AI should use it",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "What this parameter means"
            }
        },
        "required": ["param1"]
    }
}

async def execute(params: dict) -> dict[str, Any]:
    """
    Detailed docstring explaining:
    - What this tool does
    - When the AI agent should call it
    - What it returns
    """
    try:
        # Tool logic here
        pass
    except Exception as e:
        return {"error": str(e), "success": False}

REGISTER IN MCP SERVER (backend/mcp/server.py):
- Import the new tool
- Add TOOL_DEFINITION to tools list
- Add tool name to execute_tool() routing function

AGENT TRACE LOG:
Every tool execution must print a formatted trace:
print(f"""
[MCP TOOL CALLED]
Tool: {tool_name}
Input: {params}
Output: {result}
Time: {elapsed}ms
""")

ALSO UPDATE:
- Add tool to README.md MCP Tools table
- Add example of when AI would call this tool

After creating:
1. Show complete tool file
2. Show updated mcp/server.py with registration
3. Show example of how Gemini will call this tool in a conversation
4. Test the tool with sample input and show expected output