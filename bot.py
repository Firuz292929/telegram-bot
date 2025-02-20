import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

TOKEN = "7803005399:AAEGlr7esGxUD8rk-G-j4oVXeSm7G8OGjYA"
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("📦 Адрес складов"), KeyboardButton("💰 Цены"))
main_keyboard.add(KeyboardButton("🔍 Проверка трек-кода"), KeyboardButton("🖼 Поиск по фото"))
main_keyboard.add(KeyboardButton("🎓 Бесплатное обучение"), KeyboardButton("✅ Завершённые товары"))
main_keyboard.add(KeyboardButton("🌍 Изменить язык"), KeyboardButton("👤 Мой профиль"))

class Registration(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_pinduoduo_phone = State()

users_data = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("👋 Салом! Ман ISL. Чӣ кӯмак кунам?", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "📦 Адрес складов")
async def warehouse_address(message: types.Message):
    address_text = (
        "🏢 **Адрес склада в Китае:**\n\n"
        "📌 **收货人:** ISL DUSHANBE\n"
        "📞 **联系:** 13020143323\n"
        "📍 **地址:** 浙江省金华市义乌市兴港小区98栋5单元203室\n\n"
        "📦 (Dushanbe, номер, name)"
    )
    await message.answer(address_text, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "💰 Цены")
async def send_prices(message: types.Message):
    await message.answer("💵 Нархҳо: 1 кг = 20 сомонӣ")

@dp.message_handler(lambda message: message.text == "🔍 Проверка трек-кода")
async def ask_tracking_code(message: types.Message):
    await message.answer("🔢 Лутфан трек-коди худро ворид кунед.")

@dp.message_handler(lambda message: len(message.text) > 5 and message.text.isalnum())
async def track_package(message: types.Message):
    track_url = f"https://t.17track.net/ru#nums={message.text}"
    await message.answer(f"📦 Трек-коди шумо: [{message.text}]({track_url})", parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "🖼 Поиск по фото")
async def ask_for_photo(message: types.Message):
    await message.answer("📸 Лутфан акси маҳсулотро фиристед.")

@dp.message_handler(lambda message: message.text == "🎓 Бесплатное обучение")
async def free_learning(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📚 Перейти к обучению", url="https://t.me/Isl_Cargo_Urok"))
    await message.answer("🎓 Барои омӯзиш, лутфан тугмаро зер кунед:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "✅ Завершённые товары")
async def completed_orders(message: types.Message):
    await message.answer("📦 Ин рӯйхати молҳое мебошад, ки аллакай супорида шудаанд.")

@dp.message_handler(lambda message: message.text == "🌍 Изменить язык")
async def change_language(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇹🇯 Тоҷикӣ"), KeyboardButton("🇬🇧 English"))
    await message.answer("🌍 Лутфан забони худро интихоб кунед:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "👤 Мой профиль")
async def my_profile(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_data:
        profile_info = (
            f"👤 **Профили шумо:**\n\n"
            f"📌 **Ном ва Насаб:** {users_data[user_id]['full_name']}\n"
            f"📲 **Рақами Pinduoduo:** {users_data[user_id]['pinduoduo_phone']}"
        )
    else:
        profile_info = "🚀 Шумо ҳоло бақайд гирифта нашудаед! Лутфан '📌 Бақайдгирӣ'-ро пахш кунед."

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📌 Бақайдгирӣ", callback_data="register"),
        InlineKeyboardButton("✏️ Иваз кардани ном", callback_data="change_full_name"),
        InlineKeyboardButton("📲 Иваз кардани рақам", callback_data="change_pinduoduo_phone")
    )
    
    await message.answer(profile_info, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query_handler(lambda call: call.data == "register")
async def start_registration(call: types.CallbackQuery):
    await call.message.answer("✍ Лутфан ном ва насабатонро ворид кунед:")
    await Registration.waiting_for_full_name.set()

@dp.message_handler(state=Registration.waiting_for_full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📲 **Лутфан рақами телефони Pinduoduo-ро ворид кунед (бе +992):** 🙏")
    await Registration.waiting_for_pinduoduo_phone.set()

@dp.message_handler(state=Registration.waiting_for_pinduoduo_phone)
async def get_pinduoduo_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    users_data[user_id] = {
        "full_name": user_data["full_name"],
        "pinduoduo_phone": message.text
    }
    
    await message.answer("✅ Бақайдгирӣ анҷом ёфт! Акнун шумо метавонед профили худро бинед.")
    await state.finish()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)