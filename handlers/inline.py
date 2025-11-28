from aiogram import Router
import random
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import P1_NAME, P2_NAME, P1_KEY, P2_KEY
from storage import load_data
from texts import generate_text, generate_places_text, generate_zoo_text
from keyboards import get_keyboard, get_places_filter_keyboard

router = Router()


@router.inline_query()
async def inline_handler(query: InlineQuery):
    data = load_data()
    query_text = query.query.strip()

    results = []

    text_content = generate_text(data)

    if query_text.isdigit():
        amount = int(query_text)

        custom_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Добавить +{amount} {P1_NAME}",
                        callback_data=f"add_{P1_KEY}_{amount}",
                    ),
                    InlineKeyboardButton(
                        text=f"Добавить +{amount} {P2_NAME}",
                        callback_data=f"add_{P2_KEY}_{amount}",
                    ),
                ]
            ]
        )

        results.append(
            InlineQueryResultArticle(
                id="custom_add",
                title=f"Добавить {amount} баллов",
                description=f"Нажми, чтобы выбрать кому начислить {amount}",
                input_message_content=InputTextMessageContent(
                    message_text=text_content,
                    parse_mode="Markdown",
                ),
                reply_markup=custom_kb,
            )
        )
    else:
        results.append(
            InlineQueryResultArticle(
                id="main_score_v2",
                title="Показать текущий счёт",
                description=f"{P1_NAME}: {data[P1_KEY]['score']} | {P2_NAME}: {data[P2_KEY]['score']}",
                input_message_content=InputTextMessageContent(
                    message_text=text_content,
                    parse_mode="Markdown",
                ),
                reply_markup=get_keyboard(),
            )
        )

        question_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💬 Вопрос для разговора",
                        callback_data="chat_question",
                    )
                ]
            ]
        )

        results.append(
            InlineQueryResultArticle(
                id="chat_question_entry_v1",
                title="Вопрос для разговора",
                description="Сгенерировать тёплый вопрос для чата",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        "Нажми кнопку ниже, чтобы сгенерировать один тёплый вопрос "
                        "для вашего разговора."
                    ),
                    parse_mode="Markdown",
                ),
                reply_markup=question_kb,
            )
        )

        # По умолчанию в inline показываем список непосещённых мест
        data_places = load_data()
        all_places = data_places.get("places", [])
        unvisited = [p for p in all_places if not p.get("visited", False)]

        orig_places = data_places.get("places", [])
        data_places["places"] = unvisited
        places_text = generate_places_text(data_places)
        data_places["places"] = orig_places

        results.append(
            InlineQueryResultArticle(
                id="places_list",
                title="Список мест для желаний",
                description="Непосещённые и посещённые места",
                input_message_content=InputTextMessageContent(
                    message_text=places_text,
                    parse_mode="Markdown",
                ),
                reply_markup=get_places_filter_keyboard("unvisited"),
            )
        )

        # Полный список зоопарка
        data_zoo = load_data()
        zoo_text = generate_zoo_text(data_zoo)

        results.append(
            InlineQueryResultArticle(
                id="zoo_list",
                title="Зоопарк желаний",
                description="Все животные из вашего зоопарка",
                input_message_content=InputTextMessageContent(
                    message_text=zoo_text,
                    parse_mode="Markdown",
                ),
            )
        )

        # Рандом 1 или 2
        rnd = random.randint(1, 2)
        results.append(
            InlineQueryResultArticle(
                id="random_1_2",
                title="Случайное число 1 или 2",
                description="Милый рандом 1/2",
                input_message_content=InputTextMessageContent(
                    message_text=f"Сегодня выпало: *{rnd}*",
                    parse_mode="Markdown",
                ),
            )
        )

    await query.answer(results, cache_time=1, is_personal=True)
