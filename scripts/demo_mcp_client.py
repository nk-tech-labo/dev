import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_params = StdioServerParameters(command="python", args=["-m", "mcp_server"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("contract_check:")
            result = await session.call_tool(
                "contract_check",
                {"contract_id": "C-10001", "contract_name": "田中 太郎"},
            )
            print(result)

            print("get_onu_router_name:")
            result = await session.call_tool("get_onu_router_name", {"contract_id": "C-10001"})
            print(result)

            print("line_test:")
            result = await session.call_tool("line_test", {"contract_id": "C-10001"})
            print(result)

            print("get_router_shipping_address:")
            result = await session.call_tool(
                "get_router_shipping_address", {"contract_id": "C-10001"}
            )
            print(result)

            print("create_case:")
            result = await session.call_tool(
                "create_case",
                {
                    "contract_name": "田中 太郎",
                    "contract_id": "C-10001",
                    "onu_router_name": "ONU-AX1800",
                    "lamp_status": {
                        "power": "on",
                        "optical": "blink",
                        "internet": "off",
                        "alarm": "off",
                    },
                    "shipping_address": "東京都港区芝公園1-1-1",
                    "shipping_date": "2025-01-31",
                },
            )
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
