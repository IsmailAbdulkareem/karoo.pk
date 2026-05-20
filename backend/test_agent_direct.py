import asyncio
from agents.karoo_agent import chat_with_agent

async def test():
    print("Testing chat_with_agent...")
    res = await chat_with_agent("hi", [], "user")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
