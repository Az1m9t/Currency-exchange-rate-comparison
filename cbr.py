import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
import time


class CBRFetcher:
    """Класс для асинхронного получения курса USD/RUB с сайта ЦБ РФ (XML_daily.asp)"""

    BASE_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Referer": "https://www.cbr.ru/",
    }

    async def fetch_exchange_rate(self, currency_code="USD") -> str:
        """Асинхронный метод для получения курса валюты по коду (по умолчанию USD)"""
        # Запрос без параметров вернёт актуальный курс (обычно на следующий день после 11:30)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, headers=self.HEADERS) as response:
                if response.status == 200:
                    xml_text = await response.text(encoding='windows-1251')
                    return self.parse_currency_from_xml(xml_text, currency_code)
                else:
                    return f"❌ Ошибка запроса: {response.status}"

    def parse_currency_from_xml(self, xml_text: str, currency_code: str) -> str:
        """Парсит XML и возвращает курс указанной валюты"""
        try:
            tree = ET.fromstring(xml_text)
            for valute in tree.findall("Valute"):
                code = valute.find("CharCode").text
                if code == currency_code.upper():
                    value = float(valute.find("Value").text.replace(",", "."))
                    nominal = int(valute.find("Nominal").text)
                    return value
            return f"❌ Валюта {currency_code} не найдена"
        except Exception as e:
            return f"❌ Ошибка парсинга XML: {e}"


async def main():
    fetcher = CBRFetcher()
    rate = await fetcher.fetch_exchange_rate("USD")
    print(f"✅ Актуальный курс USD/RUB: {rate}")


# Запуск асинхронного кода
asyncio.run(main())
