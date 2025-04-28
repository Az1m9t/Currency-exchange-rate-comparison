import websocket
import threading
import time
import json
import re

class InvestingFetcher:
    def __init__(self):
        self.url = "wss://streaming.forexpros.com/echo/114/srbt2ucz/websocket"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.last_numeric = 82.5034
        self.ws = None

        # Сообщение для подписки
        self.subscribe_message = [
            "{\"_event\":\"bulk-subscribe\",\"tzID\":8,\"message\":\"isOpenExch-2:%%isOpenExch-1:%%pid-13994:%%isOpenExch-NaN:%%pid-6497:%%pid-6369:%%pid-1166239:%%pid-251:%%pid-6408:%%pid-26490:%%pid-252:%%pid-16678:%%pid-6435:%%pid-100160:%%pid-17195:%%pid-8274:%%pid-8359:%%pid-6407:%%pid-8849:%%isOpenExch-1004:%%pid-8833:%%pid-8862:%%pid-8830:%%pid-8836:%%pid-8831:%%pid-8916:%%pid-1175152:%%isOpenExch-152:%%pid-1175153:%%pid-169:%%pid-166:%%pid-14958:%%pid-44336:%%isOpenExch-97:%%pid-8827:%%pid-23705:%%pid-23706:%%pid-23703:%%pid-23698:%%pid-8880:%%isOpenExch-118:%%pid-8895:%%pid-1141794:%%pid-13063:%%pid-941155:%%pid-20:%%pid-172:%%isOpenExch-4:%%pid-27:%%isOpenExch-3:%%pid-167:%%isOpenExch-9:%%pid-178:%%isOpenExch-20:%%pid-1:%%isOpenExch-1002:%%pid-2:%%pid-3:%%pid-5:%%pid-7:%%pid-9:%%pid-10:%%pid-8832:%%pid-2186:%%pid-104412:%%pid-962711:%%pid-1156303:%%pid-1089835:%%pidExt-2186:%%pid-1057391:%%pid-1061443:%%pid-1061453:%%pid-1057392:%%cmt-1-5-2186:%%pid-7997:%%pid-7992:%%pid-16889:%%pid-1010718:%%pid-20176:%%pid-24497:%%pid-1073753:%%pid-13311:%%pid-1010776:%%pid-1055297:%%pid-1058142:%%pid-1061477:%%pid-1062537:%%pid-1114630:%%pid-1161529:%%pid-1177183:%%pid-989523:%%pid-8656:%%pid-44119:%%pid-100809:%%pid-942125:%%pid-1177698:%%pid-283:%%pid-386:%%pid-8136:%%pid-20224:%%pid-20870:%%pid-29731:%%pid-44408:%%pid-66:%%pid-1691:%%pid-2111:%%pid-18:%%pid-1057388:\"}"
        ]

    def on_message(self, ws, message):
        if "pid-2186" in message:
            match = re.search(r'a\[(.*)\]', message)
            if not match:
                return

            cleaned_message = match.group(1)

            try:
                first_level_data = json.loads(cleaned_message)
            except json.JSONDecodeError:
                return

            if isinstance(first_level_data, str):
                try:
                    first_level_data = json.loads(first_level_data)
                except json.JSONDecodeError:
                    return

            if not isinstance(first_level_data, dict) or "message" not in first_level_data:
                return

            msg_str = first_level_data["message"]

            if "pid-2186::" not in msg_str:
                return

            try:
                key, value = msg_str.split("::", 1)
                pid_data = json.loads(value)
                if "last_numeric" in pid_data:
                    self.last_numeric = pid_data["last_numeric"]
                    print(f"pid-2186 last_numeric: {self.last_numeric}")
            except Exception:
                pass

        # КАЖДЫЙ РАЗ отправляем подписку снова (как у тебя было)
        for msg in self.subscribe_message:
            try:
                ws.send(msg)
                #print("Resent subscription to keep connection alive")
            except Exception as e:
                print(f"Failed to resend subscription: {e}")

    def on_open(self, ws):
        print("WebSocket connected")
        for msg in self.subscribe_message:
            ws.send(msg)
        print("Initial subscription sent")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket closed: {close_status_code} {close_msg}")

    def run(self):
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    header=[f"{k}: {v}" for k, v in self.headers.items()],
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                self.ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                print(f"Exception in WebSocket: {e}")
            time.sleep(5)

    def get_last_numeric(self):
        return self.last_numeric


