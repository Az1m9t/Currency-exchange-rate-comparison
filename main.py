import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from cbr import CBRFetcher
from profinance import ProFinanceFetcher
from rapira import RapiraFetcher
from invest_rep import InvestingFetcher
import threading


# Ваш Telegram токен (замените на свой)
TOKEN = "TOKEN"


# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()  
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📉 Rates")] 
    ],
    resize_keyboard=True
)

investing_fetcher = InvestingFetcher()
async def get_all_rates():
    cbr_fetcher = CBRFetcher()
    profinance_fetcher = ProFinanceFetcher()
    abcex_fetcher = RapiraFetcher()


    # Запускаем запросы одновременно
    cbr_rate, profinance_rate, abcex_rate = await asyncio.gather(
        cbr_fetcher.fetch_exchange_rate(),
        profinance_fetcher.fetch_exchange_rate(),
        abcex_fetcher.fetch_exchange_rate(),
    )
    investing_rate = investing_fetcher.get_last_numeric()

    print(abcex_rate, cbr_rate, profinance_rate, investing_rate)

    try:
        abcex_rate = float(abcex_rate)
        cbr_rate = float(cbr_rate)
        profinance_rate = float(profinance_rate)
        investing_rate = float(investing_rate)

    except ValueError:
        return "❌ Ошибка: Один из курсов не удалось преобразовать в число"

    # Рассчитываем спред от Abcex
    cbr_spread = ((abcex_rate - cbr_rate) / abcex_rate) * 100
    profinance_spread = ((abcex_rate - profinance_rate) / abcex_rate) * 100
    investing_spread = ((abcex_rate - investing_rate) / abcex_rate) * 100
    message = f"""
📊 *Rates Summary* 📈

🔹 *Rapira rate:* `{abcex_rate:.4f}`

🔸 *CBR rate:* `{cbr_rate:.4f}` | *Spread:* `{cbr_spread:.4f}%`
🔸 *ProFinance rate:* `{profinance_rate:.4f}` | *Spread:* `{profinance_spread:.4f}%`
🔸 *Investing rate:* `{investing_rate:.4f}` | *Spread:* `{investing_spread:.4f}%`
    """
    print(message)
    # Формируем сообщение
    return message


@router.message(Command("start"))
async def start(message: types.Message):
    """Приветственное сообщение"""
    await message.answer("👋 Привет! Нажмите /rates, чтобы получить актуальные курсы.", reply_markup=keyboard)

@router.message(Command("rates"))
@router.message(lambda message: message.text == "📉 Rates")
async def send_rates(message: types.Message):
    """Отправляет курсы валют по команде /rates"""
    rates = await get_all_rates()
    await message.answer(rates, parse_mode="Markdown")

async def main():
    """Запуск бота"""
    dp.include_router(router) 

    threading.Thread(target=investing_fetcher.run, daemon=True).start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
