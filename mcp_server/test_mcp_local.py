import asyncio

from mcp.client import ClientSession
from mcp.client.stdio import stdio_client


async def main() -> None:
    async with stdio_client("python mcp_server.py") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            contract_ok = await session.call_tool(
                "contract_check",
                {"contract_number": "CN-10001", "contract_name": "佐藤太郎"},
            )
            router_name = await session.call_tool(
                "get_onu_router_name",
                {"contract_number": "CN-10001"},
            )
            lamp_status = await session.call_tool(
                "run_line_test",
                {"contract_number": "CN-10001"},
            )
            address = await session.call_tool(
                "get_router_shipping_address",
                {"contract_number": "CN-10001"},
            )
            case_result = await session.call_tool(
                "create_case",
                {
                    "customer_name": "佐藤太郎",
                    "contract_number": "CN-10001",
                    "router_name": router_name.content,
                    "router_lamp_status": lamp_status.content,
                    "shipping_address": address.content,
                    "shipping_date": "2025-04-01",
                },
            )
            print("contract_check:", contract_ok.content)
            print("router_name:", router_name.content)
            print("lamp_status:", lamp_status.content)
            print("shipping_address:", address.content)
            print("case_result:", case_result.content)


if __name__ == "__main__":
    asyncio.run(main())
