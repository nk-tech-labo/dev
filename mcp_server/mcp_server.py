from __future__ import annotations

from datetime import datetime
from typing import Dict

from mcp.server.fastmcp import FastMCP

from mock_data import CASES, CONTRACTS, ROUTER_LAMP_STATUS, ROUTER_SHIPPING_ADDRESSES, next_case_id

mcp = FastMCP("ai-ivr-servicenow")


@mcp.tool()
def contract_check(contract_number: str, contract_name: str) -> bool:
    """契約番号と契約氏名が一致するかを確認します。"""
    record = CONTRACTS.get(contract_number)
    return bool(record and record["contract_name"] == contract_name)


@mcp.tool()
def get_onu_router_name(contract_number: str) -> str:
    """契約番号から ONU ルーター名を返します。"""
    record = CONTRACTS.get(contract_number)
    if not record:
        return ""
    return record["router_name"]


@mcp.tool()
def run_line_test(contract_number: str) -> Dict[str, str]:
    """回線試験を実行し、ルーターのランプ点灯状態を返します。"""
    record = CONTRACTS.get(contract_number)
    if not record:
        return {}
    router_name = record["router_name"]
    return ROUTER_LAMP_STATUS.get(router_name, {})


@mcp.tool()
def get_router_shipping_address(contract_number: str) -> str:
    """契約番号からルーター送付先住所を返します。"""
    return ROUTER_SHIPPING_ADDRESSES.get(contract_number, "")


@mcp.tool()
def create_case(
    customer_name: str,
    contract_number: str,
    router_name: str,
    router_lamp_status: Dict[str, str],
    shipping_address: str,
    shipping_date: str,
) -> Dict[str, str]:
    """ケース起票を行い、ケース番号を返します。"""
    case_id = next_case_id()
    CASES.append(
        {
            "case_id": case_id,
            "customer_name": customer_name,
            "contract_number": contract_number,
            "router_name": router_name,
            "router_lamp_status": str(router_lamp_status),
            "shipping_address": shipping_address,
            "shipping_date": shipping_date,
            "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        }
    )
    return {"case_id": case_id}


if __name__ == "__main__":
    mcp.run()
