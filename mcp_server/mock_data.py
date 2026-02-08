from __future__ import annotations

from datetime import date
from typing import Dict, List

CONTRACTS: Dict[str, Dict[str, str]] = {
    "CN-10001": {"contract_name": "佐藤太郎", "router_name": "ONU-AX12"},
    "CN-10002": {"contract_name": "鈴木花子", "router_name": "ONU-BX200"},
    "CN-10003": {"contract_name": "田中一郎", "router_name": "ONU-CX90"},
}

ROUTER_LAMP_STATUS: Dict[str, Dict[str, str]] = {
    "ONU-AX12": {
        "power": "on",
        "optical": "blink",
        "alarm": "off",
        "lan": "on",
    },
    "ONU-BX200": {
        "power": "on",
        "optical": "on",
        "alarm": "off",
        "lan": "off",
    },
    "ONU-CX90": {
        "power": "off",
        "optical": "off",
        "alarm": "on",
        "lan": "off",
    },
}

ROUTER_SHIPPING_ADDRESSES: Dict[str, str] = {
    "CN-10001": "東京都千代田区1-2-3",
    "CN-10002": "大阪府大阪市北区4-5-6",
    "CN-10003": "福岡県福岡市中央区7-8-9",
}

CASES: List[Dict[str, str]] = []


def next_case_id() -> str:
    sequence = len(CASES) + 1
    return f"CASE-{date.today().strftime('%Y%m%d')}-{sequence:03d}"
