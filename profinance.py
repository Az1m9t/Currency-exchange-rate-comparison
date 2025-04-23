import aiohttp
import asyncio
import re

class ProFinanceFetcher:
    """Класс для асинхронного получения курса USD/RUB с ProFinance"""

    BASE_URL = "https://jq.profinance.ru/html/htmlquotes/q"

    HEADERS = {
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="133", "Not(A:Brand";v="99"',
        "Content-Type": "text/plain;charset=UTF-8",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.profinance.ru",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.profinance.ru/",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i"
    }

    async def fetch_session_id(self, session):
        """Асинхронно получает SID для запроса"""
        async with session.get(self.BASE_URL, headers=self.HEADERS) as response:
            if response.status == 200:
                resp = await response.text()
                # print(resp)
                return resp
            return None

    async def fetch_exchange_rate(self):
        """Асинхронно получает курс USD/RUB"""
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            sid = await self.fetch_session_id(session)
            if not sid:
                return "❌ Ошибка получения SID"

            # Формируем `payload` для второго запроса
            payload = f"""1;SID={sid};B=;A=;LP=;NCH=;NCHP=;S=29;S=30;S=CNY/RUB;S=RUB_FUT;S=ERUB_FUT;S=CNYRUB_FUT;S=USD/RUB_FX;S=EUR/RUB_FX;S=CNH/RUB_FX;S=USDRUB_F;S=EURRUB_F;S=CNYRUB_F;S=USD/RUB_FX1;
"""

            async with session.post(self.BASE_URL, data=payload) as response:
                if response.status == 200:
                    text_response = await response.text()
                    # print(text_response)
                    cleaned_text = re.sub(r'[+-]', '', text_response)
                    # print(cleaned_text)
                    return self.extract_usd_rub(cleaned_text)
                return f"❌ Ошибка запроса: {response.status}"

    @staticmethod
    def extract_usd_rub(text):
        """Извлекает значение B для S=USD/RUB"""
        # print(text)
        match = re.search(r"S=USD/RUB;.*?B=([\d.]+)", text)
        return match.group(1) if match else "❌ Курс USD/RUB не найден"

# async def main():
#     fetcher = ProFinanceFetcher()
#     rate = await fetcher.fetch_exchange_rate()
#     print(f"✅ Актуальный курс USD/RUB: {rate}")
#
# # Запуск асинхронного кода
# asyncio.run(main())
