import aiohttp
import asyncio

class AbcexFetcher:
    """Класс для асинхронного получения курса USDTRUB с abcex.io"""

    BASE_URL = "https://abcex.io/api/v1/exchange/public/market-data/order-book/depth?marketId=USDTRUB&lang=ru"

    async def fetch_exchange_rate(self):
        """Асинхронно получает курс USDTRUB"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.extract_price(data)
                return f"❌ Ошибка запроса: {response.status}"

    @staticmethod
    def extract_price(data):
        """Извлекает первую цену ask (цена продажи)"""
        return data.get("ask", [{}])[0].get("price", "❌ Курс USDTRUB не найден")

# async def main():
#     fetcher = AbcexFetcher()
#     rate = await fetcher.fetch_exchange_rate()
#     print(f"✅ Актуальный курс USDTRUB: {rate}")
#
# # Запуск асинхронного кода
# asyncio.run(main())
