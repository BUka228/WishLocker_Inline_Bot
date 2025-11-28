from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import P1_NAME, P2_NAME, P1_KEY, P2_KEY, EMOJI_WISH, EMOJI_HEART


def get_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text=f"+1 {P1_NAME}", callback_data=f"add_{P1_KEY}_1"),
            InlineKeyboardButton(text=f"+1 {P2_NAME}", callback_data=f"add_{P2_KEY}_1"),
        ],
        [
            InlineKeyboardButton(text=f"-1 {P1_NAME}", callback_data=f"add_{P1_KEY}_-1"),
            InlineKeyboardButton(text=f"-1 {P2_NAME}", callback_data=f"add_{P2_KEY}_-1"),
        ],
        [
            InlineKeyboardButton(text="⭐ +1 Обоим", callback_data="add_both_1"),
        ],
        [
            InlineKeyboardButton(
                text=f"Потратить {EMOJI_WISH} {P1_NAME}", callback_data=f"spend_{P1_KEY}"
            ),
            InlineKeyboardButton(
                text=f"Потратить {EMOJI_WISH} {P2_NAME}", callback_data=f"spend_{P2_KEY}"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_places_keyboard(data) -> InlineKeyboardMarkup:
    places = data.get("places", [])

    if not places:
        # Для inline-режима не показываем кнопку добавления, просто пустая клавиатура
        return InlineKeyboardMarkup(inline_keyboard=[])

    rows = []
    for place in places:
        place_id = place.get("id")
        title = place.get("title", "Без названия")
        visited = place.get("visited", False)
        status_emoji = "✅" if visited else "⭕"

        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{status_emoji} {title}",
                    callback_data=f"place_toggle_{place_id}",
                ),
                InlineKeyboardButton(
                    text="✖",
                    callback_data=f"place_delete_{place_id}",
                ),
                InlineKeyboardButton(
                    text="✏️",
                    callback_data=f"place_edit_{place_id}",
                ),
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="📋 Места"),
            KeyboardButton(text="➕ Добавить место"),
        ],
        [
            KeyboardButton(text="🔍 Непосещённые"),
            KeyboardButton(text="✨ Посещённые"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_places_filter_keyboard(active: str) -> InlineKeyboardMarkup:
    """Клавиатура для inline-сообщения со списком мест.

    active: "unvisited" или "visited" — какая вкладка сейчас активна.
    """

    unvisited_text = "🔍 Непосещённые" if active == "unvisited" else "Непосещённые"
    visited_text = "✨ Посещённые" if active == "visited" else "Посещённые"

    kb = [
        [
            InlineKeyboardButton(
                text=unvisited_text,
                callback_data="places_filter_unvisited",
            ),
            InlineKeyboardButton(
                text=visited_text,
                callback_data="places_filter_visited",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
