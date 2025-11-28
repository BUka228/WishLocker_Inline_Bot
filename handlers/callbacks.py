from datetime import datetime

import aiohttp
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import (
    P1_KEY,
    P2_KEY,
    P1_NAME,
    P2_NAME,
    EMOJI_WISH,
    OPENROUTER_API_KEY,
)
from storage import load_data, save_data
from texts import generate_text
from keyboards import get_keyboard

router = Router()


async def generate_chat_question() -> str:
    if not OPENROUTER_API_KEY:
        return "Не настроен ключ OpenRouter. Добавь OPENROUTER_API_KEY в переменные окружения."

    models = [
        "x-ai/grok-4.1-fast:free",
        "qwen/qwen3-235b-a22b:free",
        "tngtech/deepseek-r1t-chimera:free",
        "google/gemma-3-27b-it:free",
    ]

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "Ты придумываешь один интересный вопрос для разговора"
        "в личном чате. Вопрос должен быть по-русски, без обращения по имени, "
        "без перечисления вариантов, просто одно или несколько предложений"
    )

    async with aiohttp.ClientSession() as session:
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": "Придумай один вопрос для разговора.",
                    },
                ],
                "max_tokens": 128,
                "temperature": 0.9,
            }

            try:
                async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                    choices = data.get("choices") or []
                    if not choices:
                        continue
                    content = choices[0]["message"]["content"].strip()
                    if content:
                        return content
            except Exception:
                continue

    return "Сейчас не получается придумать вопрос. Попробуй ещё раз чуть позже."


@router.callback_query(F.data.startswith("add_"))
async def points_handler(callback: CallbackQuery):
    action = callback.data.split("_")
    data = load_data()
    msg = ""

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
        msg = f"{name}: {'+' if amt > 0 else ''}{amt} очков!"

    for key in [P1_KEY, P2_KEY]:
        if data[key]["score"] >= 100:
            data[key]["score"] = 0
            data[key]["wishes"] += 1
            name = P1_NAME if key == P1_KEY else P2_NAME
            msg = f"🎉 УРА! {name} получает желание! {EMOJI_WISH}"

    save_data(data)

    current_time = datetime.now().strftime("%H:%M:%S")

    try:
        new_text = generate_text(data, f"{msg} (обн. {current_time})")
        if callback.message:
            await callback.message.edit_text(
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown",
            )
        else:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown",
            )
    except Exception:
        await callback.answer("Счет изменен!", show_alert=False)
        return

    await callback.answer()


@router.callback_query(F.data == "chat_question")
async def chat_question_handler(callback: CallbackQuery):
    await callback.answer("Генерирую вопрос...", show_alert=False)

    question = await generate_chat_question()

    try:
        if callback.message:
            await callback.message.edit_text(text=question)
        else:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=question,
            )
    except Exception:
        await callback.answer("Не получилось обновить сообщение с вопросом", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.startswith("spend_"))
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
                parse_mode="Markdown",
            )
        else:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=new_text,
                reply_markup=get_keyboard(),
                parse_mode="Markdown",
            )
    else:
        await callback.answer(
            "Недостаточно желаний! Зарабатывай баллы! 🥺", show_alert=True
        )
        return

    await callback.answer()
