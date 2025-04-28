import aiohttp
import asyncio
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class CBRFetcher:

    HEADERS = {
        "Host": "www.cbr.ru",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept": "*/*",
        "Sec-Ch-Ua": '"Chromium";v="133", "Not(A:Brand";v="99"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.cbr.ru/",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i"
    }

    def __init__(self):
        self.base_url = self._generate_url()

    def _generate_url(self) -> str:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=4)
        date1 = start_date.strftime("%d/%m/%Y")
        date2 = end_date.strftime("%d/%m/%Y")
        return (
            f"https://www.cbr.ru/scripts/XML_dynamic.asp?"
            f"date_req1={date1}&date_req2={date2}&VAL_NM_RQ=R01235"
        )

    async def fetch_exchange_rate(self) -> float | str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, headers=self.HEADERS) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    print(xml_data)
                    try:
                        root = ET.fromstring(xml_data)
                        records = root.findall("Record")
                        if not records:
                            return "❌ Нет данных"
                        last_record = records[-1]
                        value_str = last_record.find("Value").text.replace(",", ".")
                        return float(value_str)
                    except Exception as e:
                        return f"❌ Ошибка парсинга XML: {e}"
                else:
                    return f"❌ Ошибка запроса: {response.status}"


