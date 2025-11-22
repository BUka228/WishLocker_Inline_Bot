import asyncio
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import CommandStart

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8338577808:AAEADwfNI_ZJMc5y1I5hiAs683NE3V1kJ0I"
DATA_FILE = "score_data.json"

# Имена участников
P1_NAME = "Никита"
P1_KEY = "nikita"
P2_NAME = "Даша"
P2_KEY = "dasha"

# Смайлики
EMOJI_P1 = "🐻"
EMOJI_P2 = "🐱"
EMOJI_HEART = "⭐"
EMOJI_WISH = "✨"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- РАБОТА С ДАННЫМИ ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            P1_KEY: {"score": 0, "wishes": 0},
            P2_KEY: {"score": 0, "wishes": 0}
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            P1_KEY: {"score": 0, "wishes": 0},
            P2_KEY: {"score": 0, "wishes": 0}
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ЛОГИКА ---
def generate_text(data, extra_msg=""):
    p1 = data[P1_KEY]
    p2 = data[P2_KEY]
    
    text = (
        f"{EMOJI_HEART} **Счёт Желаний** {EMOJI_HEART}\n\n"
        f"{EMOJI_P1} **{P1_NAME}:** {p1['score']} / 100\n"
        f"   └ Желания: {EMOJI_WISH} {p1['wishes']}\n\n"
        f"{EMOJI_P2} **{P2_NAME}:** {p2['score']} / 100\n"
        f"   └ Желания: {EMOJI_WISH} {p2['wishes']}\n"
    )
    if extra_msg:
        text += f"\n📢 {extra_msg}"
    return text

def get_keyboard():
    # Клавиатура для быстрого управления
    kb = [
        [
            InlineKeyboardButton(text=f"+1 {P1_NAME}", callback_data=f"add_{P1_KEY}_1"),
            InlineKeyboardButton(text=f"+1 {P2_NAME}", callback_data=f"add_{P2_KEY}_1")
        ],
        [
            InlineKeyboardButton(text=f"-1 {P1_NAME}", callback_data=f"add_{P1_KEY}_-1"),
            InlineKeyboardButton(text=f"-1 {P2_NAME}", callback_data=f"add_{P2_KEY}_-1")
        ],
        [
            InlineKeyboardButton(text="⭐ +1 Обоим", callback_data="add_both_1")
        ],
        [
            InlineKeyboardButton(text=f"Потратить {EMOJI_WISH} {P1_NAME}", callback_data=f"spend_{P1_KEY}"),
            InlineKeyboardButton(text=f"Потратить {EMOJI_WISH} {P2_NAME}", callback_data=f"spend_{P2_KEY}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- ОБРАБОТЧИКИ INLINE (Когда пишешь @botname) ---
@dp.inline_query()
async def inline_handler(query: InlineQuery):
    data = load_data()
    query_text = query.query.strip()
    
    results = []
    
    # 1. Стандартное табло (если ничего не ввели или текст)
    text_content = generate_text(data)
    
    # Если ввели число (например @bot 50)
    if query_text.isdigit():
        amount = int(query_text)
        
        # Кнопки для добавления этого числа
        custom_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"Добавить +{amount} {P1_NAME}", callback_data=f"add_{P1_KEY}_{amount}"),
                InlineKeyboardButton(text=f"Добавить +{amount} {P2_NAME}", callback_data=f"add_{P2_KEY}_{amount}")
            ]
        ])
        
        results.append(InlineQueryResultArticle(
            id="custom_add",
            title=f"Добавить {amount} баллов",
            description=f"Нажми, чтобы выбрать кому начислить {amount}",
            input_message_content=InputTextMessageContent(message_text=text_content, parse_mode="Markdown"),
            reply_markup=custom_kb
        ))
    else:
        # Просто вывод счета
        results.append(InlineQueryResultArticle(
            id="main_score",
            title="Показать текущий счёт",
            description=f"{P1_NAME}: {data[P1_KEY]['score']} | {P2_NAME}: {data[P2_KEY]['score']}",
            input_message_content=InputTextMessageContent(message_text=text_content, parse_mode="Markdown"),
            reply_markup=get_keyboard()
        ))

    await query.answer(results, cache_time=1, is_personal=True)

# --- ОБРАБОТЧИКИ КНОПОК ---
@dp.callback_query(F.data.startswith("add_"))
async def points_handler(callback: CallbackQuery):
    action = callback.data.split("_") 
    data = load_data()
    msg = ""
    
    # --- Логика счета ---
    if action[1] == "both":
        amt = int(action[2])
        data[P1_KEY]["score"] += amt
        data[P2_KEY]["score"] += amt
        msg = f"Милота! +{amt} очков каждому! 🥰"
    else:
        who = action[1]
        amt = int(action[2])
        data[who]["score"] += amt
        name = P1_NAME if who == P1_KEY else P2_NAME
        # Выбираем случайную эмоцию для разнообразия
        msg = f"{name}: {'+' if amt > 0 else ''}{amt} очков!"

    # --- Проверка на 100 баллов ---
    for key in [P1_KEY, P2_KEY]:
        if data[key]["score"] >= 100:
            data[key]["score"] = 0
            data[key]["wishes"] += 1
            name = P1_NAME if key == P1_KEY else P2_NAME
            msg = f"🎉 УРА! {name} получает желание! {EMOJI_WISH}"

    save_data(data)
    
    # --- ГЛАВНОЕ ИЗМЕНЕНИЕ ТУТ ---
    # Добавляем время, чтобы сообщение точно обновилось
    current_time = datetime.now().strftime("%H:%M:%S")
    
    try:
        new_text = generate_text(data, f"{msg} (обн. {current_time})")
        if callback.message:
            await callback.message.edit_text(
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown"
            )
    except Exception:
        # Если вдруг ошибка - просто отвечаем всплывашкой
        await callback.answer("Счет изменен!", show_alert=False)
        return

    await callback.answer() # Убирает часики с кнопки

@dp.callback_query(F.data.startswith("spend_"))
async def spend_wish_handler(callback: CallbackQuery):
    who = callback.data.split("_")[1]
    data = load_data()
    msg = ""
    
    if data[who]["wishes"] > 0:
        data[who]["wishes"] -= 1
        name = P1_NAME if who == P1_KEY else P2_NAME
        msg = f"{name} потратил(а) желание! Исполняй! 😏"
        save_data(data)
        
        new_text = generate_text(data, msg)
        if callback.message:
            await callback.message.edit_text(
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown"
            )
    else:
        await callback.answer("Недостаточно желаний! Зарабатывай баллы! 🥺", show_alert=True)
        return

    await callback.answer()

# --- ЗАПУСК ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())