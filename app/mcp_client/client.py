import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["app/mcp_server/server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()

            print("发现的 Tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            result = await session.call_tool(
                "get_interview_question",
                arguments={
                    "topic": "RAG",
                    "difficulty": "medium",
                },
            )

            print("\nTool 返回结果:")
            print(result.content)


if __name__ == "__main__":
    asyncio.run(main())