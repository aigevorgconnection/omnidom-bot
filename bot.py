import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# ── Настройки ──────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_ID = "@omnidompro"
LANDING_URL = "https://omnidom.pro/course"
PROMO_CODE = "OMNI10"  # ← замени на реальный промокод из GetCourse
PRIVACY_URL = "https://omnidom.pro/privacy"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ── Клавиатуры ─────────────────────────────────────────────────────────────────
def kb_consent() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Согласен", callback_data="consent_yes")],
        [InlineKeyboardButton(text="❌ Не согласен", callback_data="consent_no")],
        [InlineKeyboardButton(text="📄 Политика конфиденциальности", url=PRIVACY_URL)],
    ])

def kb_check() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я подписался, проверить", callback_data="check")],
        [InlineKeyboardButton(text="📢 Перейти на канал", url="https://t.me/omnidompro")],
    ])

def kb_go() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Перейти на курс", url=LANDING_URL)],
    ])


# ── Проверка подписки ──────────────────────────────────────────────────────────
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


# ── Хендлеры ───────────────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привет!\n\n"
        "Перед началом нам необходимо получить ваше согласие на обработку "
        "персональных данных в соответствии с нашей политикой конфиденциальности.\n\n"
        "Вы согласны?",
        reply_markup=kb_consent(),
    )


@dp.callback_query(F.data == "consent_yes")
async def cb_consent_yes(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()

    if await is_subscribed(callback.from_user.id):
        await send_reward(callback.from_user.id, callback.message.chat.id)
    else:
        await callback.message.answer(
            "Спасибо! 🙏\n\n"
            "Чтобы получить ссылку на курс и промокод на скидку 10%, "
            "подпишитесь на наш канал 👇",
            reply_markup=kb_check(),
        )


@dp.callback_query(F.data == "consent_no")
async def cb_consent_no(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        "Понимаем ваш выбор. 🙏\n\n"
        "Без согласия на обработку персональных данных мы не можем продолжить.\n"
        "Если передумаете — просто напишите /start"
    )


@dp.callback_query(F.data == "check")
async def cb_check(callback: CallbackQuery) -> None:
    await callback.answer()
    if await is_subscribed(callback.from_user.id):
        await callback.message.delete()
        await send_reward(callback.from_user.id, callback.message.chat.id)
    else:
        await callback.message.answer(
            "😕 Вы ещё не подписаны на канал.\n"
            "Подпишитесь и нажмите кнопку ещё раз!",
            reply_markup=kb_check(),
        )


async def send_reward(user_id: int, chat_id: int) -> None:
    await bot.send_message(
        chat_id=chat_id,
        text=(
            "🎉 Отлично, вы подписаны!\n\n"
            f"Вот ваша ссылка на курс:\n{LANDING_URL}\n\n"
            f"🎁 Ваш промокод на скидку 10%:\n"
            f"<code>{PROMO_CODE}</code>\n\n"
            "Введите его при оформлении заказа."
        ),
        parse_mode="HTML",
        reply_markup=kb_go(),
    )


# ── Запуск ─────────────────────────────────────────────────────────────────────
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
