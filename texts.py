from config import (
    EMOJI_HEART,
    EMOJI_WISH,
    EMOJI_P1,
    EMOJI_P2,
    P1_NAME,
    P2_NAME,
    P1_KEY,
    P2_KEY,
)


def generate_text(data, extra_msg: str = "") -> str:
    p1 = data[P1_KEY]
    p2 = data[P2_KEY]

    text = (
        f"{EMOJI_HEART} **Счёт желаний** {EMOJI_HEART}\n\n"
        f"{EMOJI_P1} **{P1_NAME}:** {p1['score']} / 100 ⭐\n"
        f"   └ Желания: {EMOJI_WISH} {p1['wishes']} ✨\n\n"
        f"{EMOJI_P2} **{P2_NAME}:** {p2['score']} / 100 ⭐\n"
        f"   └ Желания: {EMOJI_WISH} {p2['wishes']} ✨\n"
    )
    if extra_msg:
        text += f"\n📢 {extra_msg}"
    return text


def generate_places_text(data) -> str:
    places = data.get("places", [])

    if not places:
        return (
            f"{EMOJI_HEART} **Места для желаний** {EMOJI_HEART}\n\n"
            f"🗺️ Здесь пока пусто. Добавьте первые тёплые места, которые вы хотите посетить вместе! ✨"
        )

    lines = [f"{EMOJI_HEART} **Места для желаний** {EMOJI_HEART}", ""]

    for idx, place in enumerate(places, start=1):
        title = place.get("title", "Без названия")
        visited = place.get("visited", False)
        author = place.get("author")
        author_suffix = f"  — идея от {author}" if author else ""
        status_emoji = "✅" if visited else "📍"
        mood = " (уже было, но можно повторить 😌)" if visited else " (ещё впереди! ✨)"
        lines.append(f"{idx}. {status_emoji} {title}{author_suffix}{mood}")

    return "\n".join(lines)
