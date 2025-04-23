import asyncio
import websockets
import json
import re


class InvestingFetcher:
    def __init__(self):
        self.ws_url = "wss://streaming.forexpros.com/echo/997/vx32h4g3/websocket"
        self.subscribe_message = "{\"_event\":\"bulk-subscribe\",\"tzID\":8,\"message\":\"isOpenExch-1:%%isOpenExch-2:%%pid-1175152:%%isOpenExch-152:%%pid-1175153:%%pid-169:%%pid-166:%%pid-14958:%%pid-44336:%%isOpenExch-97:%%pid-8827:%%isOpenExch-1004:%%pid-13994:%%isOpenExch-NaN:%%pid-6497:%%pid-1166239:%%pid-6408:%%pid-16678:%%pid-26490:%%pid-252:%%pid-6435:%%pid-274:%%pid-6369:%%pid-17195:%%pid-941155:%%pid-8274:%%pid-1096032:%%pid-32306:%%pid-8849:%%pid-8833:%%pid-8862:%%pid-8830:%%pid-8836:%%pid-8831:%%pid-8916:%%pid-23705:%%pid-23706:%%pid-23703:%%pid-23698:%%pid-8880:%%isOpenExch-118:%%pid-8895:%%pid-1141794:%%pid-13063:%%pid-20:%%pid-172:%%isOpenExch-4:%%pid-27:%%isOpenExch-3:%%pid-167:%%isOpenExch-9:%%pid-178:%%isOpenExch-20:%%pid-8832:%%pid-1:%%isOpenExch-1002:%%pid-2:%%pid-3:%%pid-5:%%pid-7:%%pid-9:%%pid-10:%%pid-1691:%%pid-993160:%%pid-104399:%%pid-1089816:%%pidExt-1691:%%pid-1057391:%%pid-1061443:%%pid-1061453:%%pid-1057392:%%pid-1061448:%%cmt-1-5-1691:%%pid-945629:%%pid-1097781:%%pid-6440:%%pid-525:%%pid-1198306:%%pid-1225448:%%pid-9530:%%pid-50655:%%pid-2186:%%pid-1208082:%%pid-10290:%%pid-1623:%%pid-9298:\"}"
        self.uid_message = '[{"_event": "UID", "UID": 0}]'
        self.heartbeat_message = '[{"_event": "heartbeat", "data": "h"}]'
        self.last_numeric = None  # Хранит последнее значение last_numeric
        self.websocket = None

    async def connect(self):
        """Подключается к WebSocket, получает сообщение и сохраняет last_numeric."""
        try:
            async with websockets.connect(self.ws_url) as self.websocket:
                await self.websocket.send(self.subscribe_message)
                await self.websocket.send(self.uid_message)

                # Запускаем задачи для отправки ping и heartbeat
                heartbeat_task = asyncio.create_task(self.send_heartbeat())
                ping_task = asyncio.create_task(self.send_ping())

                # Ожидаем нужное сообщение
                await self.wait_for_target_message()

        except (websockets.ConnectionClosed, websockets.ConnectionClosedError) as e:
            print(f"Connection lost: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            # Закрываем соединение
            if self.websocket:
                await self.websocket.close()

    async def wait_for_target_message(self):
        """Ожидает сообщение с pid-2186 и сохраняет last_numeric."""
        while True:
            try:
                message = await self.websocket.recv()

                # Убираем обертку a[...]
                match = re.search(r'a\[(.*)\]', message)
                if not match:
                    continue

                cleaned_message = match.group(1)

                # Разбираем первый уровень JSON
                try:
                    first_level_data = json.loads(cleaned_message)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse first level JSON: {e}")
                    continue

                # Если first_level_data — это строка, разбираем её как JSON (второй уровень)
                if isinstance(first_level_data, str):
                    try:
                        first_level_data = json.loads(first_level_data)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse first level data as string: {e}")
                        continue

                # Проверяем, что first_level_data — это словарь и содержит ключ "message"
                if not isinstance(first_level_data, dict) or "message" not in first_level_data:
                    continue

                msg_str = first_level_data["message"]

                # Проверяем, содержит ли сообщение pid-2186
                if "pid-2186::" not in msg_str:
                    continue

                # Разделяем ключ и значение
                try:
                    key, value = msg_str.split("::", 1)
                except ValueError as e:
                    print(f"Failed to split message string: {e}")
                    continue

                # Разбираем значение как JSON (второй уровень)
                try:
                    pid_data = json.loads(value)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse second level JSON: {e}")
                    continue

                # Извлекаем last_numeric
                if "last_numeric" in pid_data:
                    self.last_numeric = pid_data["last_numeric"]
                    print(f"pid-2186 last_numeric: {self.last_numeric}")
                    break  # Выходим из цикла после получения нужного значения

            except Exception as e:
                print(f"Unexpected error processing message: {e}")
                break

    async def send_heartbeat(self):
        """Отправляет heartbeat сообщения."""
        while True:
            try:
                await asyncio.sleep(5)
                await self.websocket.send(self.heartbeat_message)
                print("Sent heartbeat")
            except websockets.ConnectionClosed:
                print("Heartbeat task stopped due to connection loss.")
                break
            except Exception as e:
                print(f"Error sending heartbeat: {e}")
                break

    async def send_ping(self):
        """Отправляет ping сообщения."""
        while True:
            try:
                await asyncio.sleep(5)
                await self.websocket.ping()
                print("Sent ping")
            except websockets.ConnectionClosed:
                print("Ping task stopped due to connection loss.")
                break
            except Exception as e:
                print(f"Error sending ping: {e}")
                break

    async def get_last_numeric(self):
        print(self.last_numeric)
        """Возвращает последнее сохраненное значение last_numeric."""
        return self.last_numeric

    async def start_fetcher(self):
        """Запускает вебсокет в бесконечном цикле"""
        while True:
            await self.connect()
            await asyncio.sleep(30)  # Переподключение каждые 30 секунд


async def main():
    client = InvestingFetcher()

    while True:
        await client.connect()  # Подключаемся и получаем значение
        print('ждем 30 секунд перед повторным подключением')
        await asyncio.sleep(30)  # Ждем 5 секунд перед повторным подключением


if __name__ == "__main__":
    asyncio.run(main())