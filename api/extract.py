import anthropic
import base64
import json
import os
from http.server import BaseHTTPRequestHandler
from supabase import create_client


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            image_b64 = data.get("image")
            if not image_b64:
                self._send_json({"error": "image フィールドがありません"}, 400)
                return

            result = extract_invoice_info(image_b64)
            save_to_supabase(result)
            self._send_json(result)

        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def extract_invoice_info(image_b64: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

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
                        "data": image_b64,
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
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


def save_to_supabase(result: dict):
    client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )
    client.table("invoices").insert({
        "recipient": result.get("宛名"),
        "date":      result.get("日付"),
        "amount":    result.get("金額"),
    }).execute()
