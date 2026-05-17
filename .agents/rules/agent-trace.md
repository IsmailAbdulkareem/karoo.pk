---
trigger: always_on
---

Every MCP tool call must print a trace log:
[TOOL] name | Input: {...} | Output: {...} | Time: Xms
Every agent decision must be logged with reasoning.
Save traces to backend/logs/ folder.
Return agent_trace field in /api/chat response.
Traces are required for hackathon judge evaluation. 