from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from storage import load_data, save_data
from texts import generate_places_text
from keyboards import get_places_keyboard, get_main_menu, get_places_filter_keyboard


router = Router()

# Простое состояние по пользователю: add_place / edit_place
user_states: dict[int, dict] = {}


@router.message(F.text.regexp(r"^/start(?:@\\w+)?$"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Здесь вы можете вести список мест для желаний.",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "📋 Места")
async def menu_places(message: Message):
    data = load_data()
    text = generate_places_text(data)
    kb = get_places_keyboard(data)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.message(F.text == "🔍 Непосещённые")
async def menu_places_unvisited(message: Message):
    data = load_data()
    places = [p for p in data.get("places", []) if not p.get("visited", False)]

    if not places:
        await message.answer("Нет непосещённых мест — всё уже исполнено или список пуст! ✨")
        return

    orig_places = data.get("places", [])
    data["places"] = places
    text = generate_places_text(data)
    data["places"] = orig_places

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "✨ Посещённые")
async def menu_places_visited(message: Message):
    data = load_data()
    places = [p for p in data.get("places", []) if p.get("visited", False)]

    if not places:
        await message.answer("Пока нет посещённых мест — всё ещё впереди! 💫")
        return

    orig_places = data.get("places", [])
    data["places"] = places
    text = generate_places_text(data)
    data["places"] = orig_places

    await message.answer(text)


@router.message(F.text == "➕ Добавить место")
async def menu_add_place_start(message: Message):
    if not message.from_user:
        return
    user_states[message.from_user.id] = {"mode": "add_place"}
    await message.answer("Напиши название нового места одним сообщением ✨")


@router.callback_query(F.data == "places_help_add")
async def places_help_add(callback: CallbackQuery):
    await callback.answer("Открой чат с ботом и используй кнопку '➕ Добавить место' в меню.", show_alert=True)


@router.callback_query(F.data.startswith("place_toggle_"))
async def place_toggle(callback: CallbackQuery):
    place_id_str = callback.data.split("_", 2)[2]
    try:
        place_id = int(place_id_str)
    except ValueError:
        await callback.answer("Что-то пошло не так", show_alert=False)
        return

    data = load_data()
    places = data.get("places", [])

    for place in places:
        if place.get("id") == place_id:
            place["visited"] = not place.get("visited", False)
            break

    data["places"] = places
    save_data(data)

    text = generate_places_text(data)
    kb = get_places_keyboard(data)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()


@router.callback_query(F.data.startswith("place_delete_"))
async def place_delete(callback: CallbackQuery):
    place_id_str = callback.data.split("_", 2)[2]
    try:
        place_id = int(place_id_str)
    except ValueError:
        await callback.answer("Что-то пошло не так", show_alert=False)
        return

    data = load_data()
    places = data.get("places", [])
    places = [p for p in places if p.get("id") != place_id]

    data["places"] = places
    save_data(data)

    text = generate_places_text(data)
    kb = get_places_keyboard(data)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer("Место удалено")


@router.callback_query(F.data.startswith("place_edit_"))
async def place_edit_hint(callback: CallbackQuery):
    place_id_str = callback.data.split("_", 2)[2]
    try:
        place_id = int(place_id_str)
    except ValueError:
        await callback.answer("Что-то пошло не так", show_alert=False)
        return
    if not callback.from_user:
        await callback.answer()
        return

    user_states[callback.from_user.id] = {"mode": "edit_place", "place_id": place_id}

    await callback.answer("Теперь отправь новое название этого места одним сообщением.", show_alert=True)


@router.callback_query(F.data == "places_filter_unvisited")
async def places_filter_unvisited(callback: CallbackQuery):
    data = load_data()
    places = [p for p in data.get("places", []) if not p.get("visited", False)]

    orig_places = data.get("places", [])
    data["places"] = places
    text = generate_places_text(data)
    data["places"] = orig_places

    try:
        if callback.message:
            await callback.message.edit_text(
                text=text,
                reply_markup=get_places_filter_keyboard("unvisited"),
                parse_mode="Markdown",
            )
        else:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=text,
                reply_markup=get_places_filter_keyboard("unvisited"),
                parse_mode="Markdown",
            )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(F.data == "places_filter_visited")
async def places_filter_visited(callback: CallbackQuery):
    data = load_data()
    places = [p for p in data.get("places", []) if p.get("visited", False)]

    orig_places = data.get("places", [])
    data["places"] = places
    text = generate_places_text(data)
    data["places"] = orig_places

    try:
        if callback.message:
            await callback.message.edit_text(
                text=text,
                reply_markup=get_places_filter_keyboard("visited"),
                parse_mode="Markdown",
            )
        else:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=text,
                reply_markup=get_places_filter_keyboard("visited"),
                parse_mode="Markdown",
            )
    except Exception:
        pass

    await callback.answer()


@router.message()
async def handle_place_states(message: Message):
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
    places = data.get("places", [])

    if mode == "add_place":
        new_id = 1
        if places:
            existing_ids = [p.get("id", 0) for p in places]
            new_id = max(existing_ids) + 1

        author_name = message.from_user.first_name if message.from_user else None

        places.append({"id": new_id, "title": text, "visited": False, "author": author_name})
        data["places"] = places
        save_data(data)

        reply_text = f"Добавлено новое место: {text}"

    elif mode == "edit_place":
        place_id = state.get("place_id")
        if place_id is None:
            return

        updated = False
        for place in places:
            if place.get("id") == place_id:
                place["title"] = text
                updated = True
                break

        if not updated:
            await message.answer("Место для редактирования не найдено")
            user_states.pop(message.from_user.id, None)
            return

        data["places"] = places
        save_data(data)
        reply_text = "Название места обновлено"
    else:
        return

    user_states.pop(message.from_user.id, None)

    full_text = generate_places_text(data)
    kb = get_places_keyboard(data)

    await message.answer(reply_text)
    await message.answer(full_text, reply_markup=kb, parse_mode="Markdown")
