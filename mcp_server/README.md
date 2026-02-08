# Foundry 用 MCP サーバー (AI-IVR ↔ ServiceNow)

このフォルダーは、市販製品 AI-IVR から ServiceNow API 相当の操作を呼び出す MCP サーバー構成の参考実装と、Microsoft の公式手順に沿った構築・検証フローをまとめたものです。外部接続が不可の環境でも MCP の動作確認ができるよう、**ローカルのダミーデータで検証できる構成**を含めています。

## Microsoft 公式手順に沿った構築フロー

> **公式手順**: [モデル コンテキスト プロトコル (MCP) サーバーをビルドして登録する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/mcp/build-your-own-mcp-server?view=foundry)

以下は、公式手順の流れに沿って整理した作業ステップです。各ステップの末尾に、**公式手順に対応する箇所**と、必要な **チューニング内容**を明記しています。

### 1. 前提条件の準備

- Foundry Agent Service が有効なプロジェクト
- Azure サブスクリプションと権限 (通常はリソースグループの共同作成者)
- Python 3.11+
- Azure Functions Core Tools v4
- Azure Developer CLI (azd)
- (任意) Azure API Center

> **公式手順に対応**: 「前提条件」節

### 2. MCP サーバー用テンプレートの取得

```bash
azd init --template remote-mcp-functions-python -e mcpserver-python
```

> **公式手順に対応**: 「Azure Functions を使用して MCP サーバーを構築する」節の `azd init` ステップ

### 3. MCP ツール定義の実装 (チューニング)

公式テンプレート生成後、MCP が公開するツール定義を以下の 5 種類に置き換えます。

| ツール名 | 入力 | 出力 | 説明 |
| --- | --- | --- | --- |
| `contract_check` | `contract_number`, `contract_name` | `bool` | 契約情報の存在確認 |
| `get_onu_router_name` | `contract_number` | `str` | ONU ルーター名取得 |
| `run_line_test` | `contract_number` | `Dict[str, str]` | 回線試験 (ランプ状態) |
| `get_router_shipping_address` | `contract_number` | `str` | ルーター送付先住所 |
| `create_case` | `customer_name`, `contract_number`, `router_name`, `router_lamp_status`, `shipping_address`, `shipping_date` | `Dict[str, str]` | ケース起票 |

> **公式手順に対応**: 「MCP サーバー関数をカスタマイズして特定の API とサービスを公開します」
> 
> **チューニング内容**: AI-IVR のシナリオに合わせてツール定義を変更 (上記 5 ツール)

テンプレート内の MCP 関数定義部分を、`mcp_server/mcp_server.py` にある関数定義に合わせる形で更新してください。

### 4. ローカルで MCP を起動して確認

```bash
func start
```

> **公式手順に対応**: 「Azure Functions Core Tools を使用して、MCP サーバーをローカルでテストします」

### 5. Azure へデプロイ

```bash
azd up
```

> **公式手順に対応**: 「Azure Developer CLI を使用して MCP サーバーを Azure にデプロイします」

### 6. (任意) API Center 登録 & Foundry から接続

必要に応じて Azure API Center に登録し、Foundry から MCP サーバーを接続します。

> **公式手順に対応**: 「Azure API Center を使用してプライベート組織ツールカタログに登録」〜「Foundry から MCP サーバーを接続」

---

## チューニングした MCP サーバー実装 (ローカル検証用)

外部接続が不可の閉域環境でも MCP の API 呼び出しを検証できるように、ローカルで動作する MCP サーバーを用意しています。`mcp_server.py` は **MCP over stdio** で実行でき、`test_mcp_local.py` で一連の API 呼び出しを検証できます。

### 1. 依存関係の準備

```bash
python -m venv .venv
source .venv/bin/activate
pip install mcp
```

### 2. MCP サーバーの起動

```bash
python mcp_server.py
```

### 3. MCP ツール呼び出し検証

別ターミナルで以下を実行します。

```bash
python test_mcp_local.py
```

> **チューニング内容**: `mock_data.py` のダミーデータを使って外部 API 呼び出しを模擬し、閉域環境でも MCP 検証ができるようにしました。

---

## ServiceNow への切り替えについて

閉域接続のみの環境では ServiceNow への外部通信ができないため、本フォルダーのローカル検証はダミーデータで実施します。運用環境で ServiceNow に切り替える場合は、`mcp_server.py` の各ツール実装で ServiceNow REST API を呼び出す実装に置き換えます。MCP のツール定義はそのまま使えるため、**テストと本番で MCP のインターフェースを共通化**できます。

---

## ファイル構成

- `mcp_server.py`: MCP ツール定義 (AI-IVR 用 5 API)
- `mock_data.py`: 閉域検証用のダミーデータ
- `test_mcp_local.py`: MCP のローカル検証用スクリプト
