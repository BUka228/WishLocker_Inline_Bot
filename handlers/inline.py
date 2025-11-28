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
from texts import generate_text, generate_places_text
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
                id="main_score",
                title="Показать текущий счёт",
                description=f"{P1_NAME}: {data[P1_KEY]['score']} | {P2_NAME}: {data[P2_KEY]['score']}",
                input_message_content=InputTextMessageContent(
                    message_text=text_content,
                    parse_mode="Markdown",
                ),
                reply_markup=get_keyboard(),
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
