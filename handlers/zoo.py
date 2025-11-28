from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from storage import load_data, save_data
from texts import generate_zoo_text
from keyboards import (
    get_zoo_keyboard,
    get_zoo_menu,
)


router = Router()

# Простое состояние по пользователю: add_animal / edit_animal
user_states: dict[int, dict] = {}


@router.message(F.text == "🦁 Зоопарк")
async def menu_zoo(message: Message):
    data = load_data()
    text = generate_zoo_text(data)
    kb = get_zoo_keyboard(data)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    await message.answer("Меню по зоопарку", reply_markup=get_zoo_menu())


@router.message(F.text == "📋 Животные")
async def zoo_list(message: Message):
    data = load_data()
    text = generate_zoo_text(data)
    kb = get_zoo_keyboard(data)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.message(F.text == "➕ Добавить животное")
async def zoo_add_start(message: Message):
    if not message.from_user:
        return
    user_states[message.from_user.id] = {"mode": "add_animal"}
    await message.answer("Напиши название нового животного одним сообщением ✨")


@router.callback_query(F.data.startswith("zoo_delete_"))
async def zoo_delete(callback: CallbackQuery):
    animal_id_str = callback.data.split("_", 2)[2]
    try:
        animal_id = int(animal_id_str)
    except ValueError:
        await callback.answer("Что-то пошло не так", show_alert=False)
        return

    data = load_data()
    animals = data.get("zoo", [])
    animals = [a for a in animals if a.get("id") != animal_id]

    data["zoo"] = animals
    save_data(data)

    text = generate_zoo_text(data)
    kb = get_zoo_keyboard(data)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer("Животное удалено")


@router.callback_query(F.data.startswith("zoo_edit_"))
async def zoo_edit_hint(callback: CallbackQuery):
    animal_id_str = callback.data.split("_", 2)[2]
    try:
        animal_id = int(animal_id_str)
    except ValueError:
        await callback.answer("Что-то пошло не так", show_alert=False)
        return
    if not callback.from_user:
        await callback.answer()
        return

    user_states[callback.from_user.id] = {"mode": "edit_animal", "animal_id": animal_id}

    await callback.answer("Теперь отправь новое название этого животного одним сообщением.", show_alert=True)




@router.message(
    F.text &
    ~F.text.regexp(r"^/") &
    ~F.text.in_(
        [
            "📋 Места",
            "➕ Добавить место",
            "🔍 Непосещённые",
            "✨ Посещённые",
            "🦁 Зоопарк",
            "📋 Животные",
            "➕ Добавить животное",
            "⬅️ В главное меню",
        ]
    )
)
async def handle_zoo_states(message: Message):
    if not message.from_user:
        return

    state = user_states.get(message.from_user.id)
    if not state:
        return

    mode = state.get("mode")
    text = (message.text or "").strip()
    if not text:
        return

    data = load_data()
    animals = data.get("zoo", [])

    if mode == "add_animal":
        new_id = 1
        if animals:
            existing_ids = [a.get("id", 0) for a in animals]
            new_id = max(existing_ids) + 1

        animals.append({"id": new_id, "title": text})
        data["zoo"] = animals
        save_data(data)

        reply_text = f"Добавлено новое животное: {text}"

    elif mode == "edit_animal":
        animal_id = state.get("animal_id")
        if animal_id is None:
            return

        updated = False
        for animal in animals:
            if animal.get("id") == animal_id:
                animal["title"] = text
                updated = True
                break

        if not updated:
            await message.answer("Животное для редактирования не найдено")
            user_states.pop(message.from_user.id, None)
            return

        data["zoo"] = animals
        save_data(data)
        reply_text = "Название животного обновлено"
    else:
        return

    user_states.pop(message.from_user.id, None)
    await message.answer(reply_text)
