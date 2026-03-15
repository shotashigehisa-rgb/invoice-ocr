#!/usr/bin/env python3
"""
請求書OCR - 請求書JPGから宛名・日付・金額を抽出するツール
使い方: python invoice_ocr.py <請求書.jpg>
"""

import anthropic
import base64
import json
import sys
from pathlib import Path


def extract_invoice_info(image_path: str) -> dict:
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "この請求書から以下の3項目を抽出してJSONのみ返してください。"
                        "見つからない場合はnullにしてください。\n\n"
                        '{"宛名": "...", "日付": "...", "金額": "..."}'
                    ),
                },
            ],
        }],
    )

    text = response.content[0].text.strip()
    # コードブロック除去
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    # JSON部分だけ取り出す
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


def main():
    if len(sys.argv) < 2:
        print("使い方: python invoice_ocr.py <請求書.jpg>")
        sys.exit(1)

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"エラー: ファイルが見つかりません: {image_path}")
        sys.exit(1)

    print(f"処理中: {image_path}")
    result = extract_invoice_info(image_path)

    print("\n=== 抽出結果 ===")
    print(f"宛名 : {result.get('宛名') or 'なし'}")
    print(f"日付 : {result.get('日付') or 'なし'}")
    print(f"金額 : {result.get('金額') or 'なし'}")

    output_path = Path(image_path).with_suffix(".json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n保存しました: {output_path}")


if __name__ == "__main__":
    main()
