# AI-IVR向け ServiceNow MCP サーバー

市販製品AI-IVRからServiceNowのAPI群を呼び出すためのMCPサーバー実装です。閉域環境でServiceNowへ直接接続できない前提のため、**モックデータでの動作確認**を標準で提供します。

## 対応ツール

| MCPツール名 | 概要 |
| --- | --- |
| `contract_check` | 契約番号・契約氏名から契約の存在確認を行う |
| `get_onu_router_name` | 契約番号からONUルーター名を取得 |
| `line_test` | 回線試験（モック）を行いランプ点灯状態を取得 |
| `get_router_shipping_address` | ルーター送付先住所を取得 |
| `create_case` | ケース起票 |

## モックデータ

`mcp_server/data/mock_data.json` に検証用の契約データを定義しています。ServiceNowに接続できない場合でも、ここにある情報を使ってMCPの呼び出し検証が可能です。

## 実行方法 (モック)

```bash
pip install -r requirements.txt
pip install mcp
python -m mcp_server
```

MCPクライアントでの簡易確認:

```bash
python scripts/demo_mcp_client.py
```

## ServiceNow接続

以下の環境変数を設定するとServiceNow APIを呼び出します。

```bash
export SERVICENOW_BASE_URL="https://your-instance.service-now.com"
export SERVICENOW_USERNAME="api_user"
export SERVICENOW_PASSWORD="api_password"
python -m mcp_server
```

※ ServiceNow APIのテーブル名・フィールド名は `u_contract` / `u_case` を前提にしています。環境に合わせて `mcp_server/server.py` 内のパスとフィールド名を変更してください。
