from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from mcp.server.fastmcp import FastMCP

DATA_PATH = Path(__file__).resolve().parent / "data" / "mock_data.json"


@dataclass
class ContractInfo:
    contract_name: str
    onu_router_name: str
    lamp_status: Dict[str, str]
    shipping_address: str


class MockRepository:
    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self._data_path = data_path
        self._contracts = self._load_contracts()

    def _load_contracts(self) -> Dict[str, ContractInfo]:
        payload = json.loads(self._data_path.read_text(encoding="utf-8"))
        contracts: Dict[str, ContractInfo] = {}
        for contract_id, info in payload.get("contracts", {}).items():
            contracts[contract_id] = ContractInfo(
                contract_name=info["contract_name"],
                onu_router_name=info["onu_router_name"],
                lamp_status=info["lamp_status"],
                shipping_address=info["shipping_address"],
            )
        return contracts

    def get_contract(self, contract_id: str) -> Optional[ContractInfo]:
        return self._contracts.get(contract_id)


class ServiceNowClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._session.headers.update({"Accept": "application/json"})

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = self._session.get(f"{self._base_url}{path}", params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._session.post(
            f"{self._base_url}{path}",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def find_contract(self, contract_id: str, contract_name: str) -> bool:
        data = self._get(
            "/api/now/table/u_contract",
            params={"sysparm_query": f"number={contract_id}^name={contract_name}"},
        )
        return bool(data.get("result"))

    def fetch_router_name(self, contract_id: str) -> Optional[str]:
        data = self._get(
            "/api/now/table/u_contract",
            params={"sysparm_query": f"number={contract_id}", "sysparm_fields": "u_onu_router"},
        )
        result = data.get("result")
        if not result:
            return None
        return result[0].get("u_onu_router")

    def fetch_shipping_address(self, contract_id: str) -> Optional[str]:
        data = self._get(
            "/api/now/table/u_contract",
            params={"sysparm_query": f"number={contract_id}", "sysparm_fields": "u_shipping_address"},
        )
        result = data.get("result")
        if not result:
            return None
        return result[0].get("u_shipping_address")

    def create_case(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/api/now/table/u_case", payload)


class ServiceLayer:
    def __init__(self, mock_repo: MockRepository, sn_client: Optional[ServiceNowClient]) -> None:
        self._mock_repo = mock_repo
        self._sn_client = sn_client

    def contract_exists(self, contract_id: str, contract_name: str) -> bool:
        if self._sn_client:
            return self._sn_client.find_contract(contract_id, contract_name)
        contract = self._mock_repo.get_contract(contract_id)
        return bool(contract and contract.contract_name == contract_name)

    def get_router_name(self, contract_id: str) -> Optional[str]:
        if self._sn_client:
            return self._sn_client.fetch_router_name(contract_id)
        contract = self._mock_repo.get_contract(contract_id)
        return contract.onu_router_name if contract else None

    def get_lamp_status(self, contract_id: str) -> Optional[Dict[str, str]]:
        contract = self._mock_repo.get_contract(contract_id)
        return contract.lamp_status if contract else None

    def get_shipping_address(self, contract_id: str) -> Optional[str]:
        if self._sn_client:
            return self._sn_client.fetch_shipping_address(contract_id)
        contract = self._mock_repo.get_contract(contract_id)
        return contract.shipping_address if contract else None

    def create_case(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self._sn_client:
            return self._sn_client.create_case(payload)
        return {
            "result": {
                "case_id": f"MOCK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "status": "created",
                "payload": payload,
            }
        }


def build_service_layer() -> ServiceLayer:
    mock_repo = MockRepository()
    base_url = os.getenv("SERVICENOW_BASE_URL")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    if base_url and username and password:
        return ServiceLayer(mock_repo, ServiceNowClient(base_url, username, password))
    return ServiceLayer(mock_repo, None)


mcp = FastMCP("ai-ivr-servicenow")
service = build_service_layer()


@mcp.tool()
def contract_check(contract_id: str, contract_name: str) -> Dict[str, Any]:
    """契約番号・契約氏名から契約存在確認を行う。"""
    exists = service.contract_exists(contract_id, contract_name)
    return {"contract_id": contract_id, "contract_name": contract_name, "exists": exists}


@mcp.tool()
def get_onu_router_name(contract_id: str) -> Dict[str, Any]:
    """契約番号からONUルーター名を取得する。"""
    router_name = service.get_router_name(contract_id)
    return {"contract_id": contract_id, "onu_router_name": router_name}


@mcp.tool()
def line_test(contract_id: str) -> Dict[str, Any]:
    """回線試験を実行し、ルーターのランプ状態を返す。"""
    lamp_status = service.get_lamp_status(contract_id)
    return {"contract_id": contract_id, "lamp_status": lamp_status}


@mcp.tool()
def get_router_shipping_address(contract_id: str) -> Dict[str, Any]:
    """契約番号からルーター送付先住所を取得する。"""
    address = service.get_shipping_address(contract_id)
    return {"contract_id": contract_id, "shipping_address": address}


@mcp.tool()
def create_case(
    contract_name: str,
    contract_id: str,
    onu_router_name: str,
    lamp_status: Dict[str, str],
    shipping_address: str,
    shipping_date: str,
) -> Dict[str, Any]:
    """ケース起票を行う。"""
    payload = {
        "contract_name": contract_name,
        "contract_id": contract_id,
        "onu_router_name": onu_router_name,
        "lamp_status": lamp_status,
        "shipping_address": shipping_address,
        "shipping_date": shipping_date,
    }
    return service.create_case(payload)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
