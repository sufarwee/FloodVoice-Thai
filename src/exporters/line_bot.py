import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_NOTIFY_TOKEN

class LineExporter:
    """Exporter สำหรับยิงการ์ดแจ้งเตือนเหตุฉุกเฉินเข้า LINE Group / LINE Official Account"""
    
    def __init__(self, channel_access_token: Optional[str] = None, notify_token: Optional[str] = None):
        self.channel_access_token = channel_access_token or LINE_CHANNEL_ACCESS_TOKEN
        self.notify_token = notify_token or LINE_NOTIFY_TOKEN

    def send_line_notify(self, message: str) -> bool:
        """ส่งข้อความด่วนผ่าน LINE Notify (ฟรีกว่า และยิงเข้ากลุ่มง่าย)"""
        if not self.notify_token:
            print("LineExporter: LINE_NOTIFY_TOKEN is missing.")
            return False
        
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {self.notify_token}"}
        data = urllib.parse.urlencode({"message": message}).encode("utf-8")
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except Exception as e:
            print(f"LineExporter error (LINE Notify): {e}")
            return False

    def send_flex_message(self, to_id: str, case_data: Dict[str, Any]) -> bool:
        """ส่งการ์ดแจ้งเตือนเหตุฉุกเฉิน Flex Message ผ่าน LINE Messaging API"""
        if not self.channel_access_token:
            print("LineExporter: LINE_CHANNEL_ACCESS_TOKEN is missing.")
            return False

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_access_token}"
        }

        urgency_color = "#FF0000" if case_data.get("urgency") == "CRITICAL" else "#FF8C00"
        
        flex_contents = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": urgency_color,
                "contents": [
                    {
                        "type": "text",
                        "text": f"🚨 แจ้งเหตุฉุกเฉิน ({case_data.get('urgency', 'HIGH')})",
                        "weight": "bold",
                        "color": "#FFFFFF",
                        "size": "md"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"📍 {case_data.get('subdistrict', '')} {case_data.get('district', '')} {case_data.get('province', '')}",
                        "weight": "bold",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": f"🏠 จุดสังเกต: {case_data.get('landmark_detail', 'ไม่ระบุ')}",
                        "wrap": True,
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"🆘 ต้องการ: {', '.join(case_data.get('needs', []))}",
                        "wrap": True,
                        "color": "#D9534F",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"📞 ติดต่อ: {case_data.get('contact_phone', 'ไม่ระบุ')}",
                        "size": "sm"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูโพสต์ต้นทาง",
                            "uri": case_data.get("source_url", "https://google.com")
                        },
                        "style": "link",
                        "size": "sm"
                    }
                ]
            }
        }

        payload = {
            "to": to_id,
            "messages": [
                {
                    "type": "flex",
                    "altText": f"🚨 แจ้งเหตุภัยพิบัติ: {case_data.get('district', '')}",
                    "contents": flex_contents
                }
            ]
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except Exception as e:
            print(f"LineExporter error (Flex Message): {e}")
            return False
