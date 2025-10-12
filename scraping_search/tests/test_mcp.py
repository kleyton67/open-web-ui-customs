import asyncio
from fastmcp import Client, FastMCP

# In-memory server (ideal for testing)
server = FastMCP("TestServer")
client = Client(server)

# HTTP server
client = Client("http://0.0.0.0:8889/mcp")


async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(f"Tools : {tools}")
        print(f"Resources: {resources}")
        
        # Execute operations
        result = await client.call_tool(name="search_web", arguments={"request": {"query": "abobora", "count": 5}})
        print(result)

asyncio.run(main())