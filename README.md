# invoice-ocr

請求書JPGから **宛名・日付・金額** を自動抽出するツールです。
Claude API（Haiku）のビジョン機能を使って文字を読み取り、JSONに保存します。

## セットアップ

```bash
pip install -r requirements.txt
```

環境変数にAPIキーをセット：

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-xxxx...

# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-xxxx...
```

## 使い方

```bash
python invoice_ocr.py 請求書.jpg
```

### 出力例

```
=== 抽出結果 ===
宛名 : 株式会社〇〇
日付 : 2024年3月15日
金額 : 110,000円

保存しました: 請求書.json
```

`請求書.json` に以下の形式で保存されます：

```json
{
  "宛名": "株式会社〇〇",
  "日付": "2024年3月15日",
  "金額": "110,000円"
}
```

## Vercelへのデプロイ

1. [Vercel](https://vercel.com/) にGitHubアカウントでログイン
2. `invoice-ocr` リポジトリをインポート
3. **Environment Variables** に以下を追加：
   - `ANTHROPIC_API_KEY` = `sk-ant-xxxx...`
4. Deploy ボタンを押すだけ

## 必要なもの

- Python 3.8+
- [Anthropic APIキー](https://console.anthropic.com/)
