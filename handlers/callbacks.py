from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import (
    P1_KEY,
    P2_KEY,
    P1_NAME,
    P2_NAME,
    EMOJI_WISH,
)
from storage import load_data, save_data
from texts import generate_text
from keyboards import get_keyboard

router = Router()


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
