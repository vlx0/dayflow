#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dayflow — console daily schedule and notes (en / ru / es)."""

from __future__ import annotations

import json
import os
import random
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_PATH = Path.home() / ".dayflow" / "data.json"
TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
LANGS = ("en", "ru", "es")
DEFAULT_LANG = "en"

# locale for date parts: weekdays Mon..Sun, months 1..12
DATE_PARTS = {
    "en": {
        "weekdays": (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ),
        "months": (
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ),
    },
    "ru": {
        "weekdays": (
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота",
            "воскресенье",
        ),
        "months": (
            "",
            "января",
            "февраля",
            "марта",
            "апреля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сентября",
            "октября",
            "ноября",
            "декабря",
        ),
    },
    "es": {
        "weekdays": (
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        ),
        "months": (
            "",
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ),
    },
}

I18N = {
    "en": {
        "pause": "Enter…",
        "today": "Today",
        "yesterday": "Yesterday",
        "tomorrow": "Tomorrow",
        "schedule": "Plan",
        "notes": "Notes",
        "empty": "—",
        "untitled": "Untitled",
        "time_prompt": "Time",
        "invalid_time": "Bad time.",
        "what_to_do": "What to do",
        "empty_title": "Empty.",
        "added": "Ok.",
        "no_tasks": "No tasks.",
        "task_number": "#",
        "invalid_number": "Bad #.",
        "marked_done": "Ok.",
        "marked_undone": "Ok.",
        "deleted": "Ok.",
        "note_title": "Title",
        "note_text": "Text (empty line = end):",
        "need_line": "Need a line.",
        "empty_note": "Empty.",
        "saved": "Ok.",
        "no_notes": "No notes.",
        "note_number": "#",
        "clear_confirm": "Clear day? (yes/no)",
        "clear_default": "no",
        "cancelled": "Cancelled.",
        "day_cleared": "Ok.",
        "date_prompt": "Date YYYY-MM-DD",
        "invalid_date": "Bad date.",
        "menu": "Menu",
        "m1": "+task",
        "m2": "-task",
        "m3": "+note",
        "m4": "-note",
        "m5": "yesterday",
        "m6": "today",
        "m7": "tomorrow",
        "m8": "date",
        "m0": "clear",
        "ml": "lang",
        "mq": "quit",
        "data": "Data",
        "choice": ">",
        "bye": "Bye!",
        "unknown": "Unknown.",
        "lang_menu": "1 en  2 ru  3 es",
        "lang_set": "Language: English.",
        "yes_words": ("yes", "y"),
    },
    "ru": {
        "pause": "Enter…",
        "today": "Сегодня",
        "yesterday": "Вчера",
        "tomorrow": "Завтра",
        "schedule": "План",
        "notes": "Распорядок",
        "empty": "—",
        "untitled": "Без названия",
        "time_prompt": "Время",
        "invalid_time": "Неверное время.",
        "what_to_do": "Что сделать",
        "empty_title": "Пусто.",
        "added": "Ок.",
        "no_tasks": "Нет задач.",
        "task_number": "№",
        "invalid_number": "Нет такого №.",
        "marked_done": "Ок.",
        "marked_undone": "Ок.",
        "deleted": "Ок.",
        "note_title": "Заголовок",
        "note_text": "Текст (пустая строка — конец):",
        "need_line": "Нужна строка.",
        "empty_note": "Пусто.",
        "saved": "Ок.",
        "no_notes": "Нет заметок.",
        "note_number": "№",
        "clear_confirm": "Очистить день? (да/нет)",
        "clear_default": "нет",
        "cancelled": "Отмена.",
        "day_cleared": "Ок.",
        "date_prompt": "Дата ГГГГ-ММ-ДД",
        "invalid_date": "Неверная дата.",
        "menu": "Меню",
        "m1": "+задача",
        "m2": "−задача",
        "m3": "+заметка",
        "m4": "−заметка",
        "m5": "вчера",
        "m6": "сегодня",
        "m7": "завтра",
        "m8": "дата",
        "m0": "очистить",
        "ml": "язык",
        "mq": "выход",
        "data": "Данные",
        "choice": ">",
        "bye": "Пока!",
        "unknown": "Нет.",
        "lang_menu": "1 en  2 ru  3 es",
        "lang_set": "Язык: русский.",
        "yes_words": ("да", "д", "yes", "y"),
    },
    "es": {
        "pause": "Enter…",
        "today": "Hoy",
        "yesterday": "Ayer",
        "tomorrow": "Mañana",
        "schedule": "Plan",
        "notes": "Notes",
        "empty": "—",
        "untitled": "Sin título",
        "time_prompt": "Hora",
        "invalid_time": "Hora inválida.",
        "what_to_do": "Qué hacer",
        "empty_title": "Vacío.",
        "added": "Ok.",
        "no_tasks": "Sin tareas.",
        "task_number": "#",
        "invalid_number": "# inválido.",
        "marked_done": "Ok.",
        "marked_undone": "Ok.",
        "deleted": "Ok.",
        "note_title": "Título",
        "note_text": "Texto (línea vacía = fin):",
        "need_line": "Falta texto.",
        "empty_note": "Vacío.",
        "saved": "Ok.",
        "no_notes": "Sin notas.",
        "note_number": "#",
        "clear_confirm": "¿Borrar día? (sí/no)",
        "clear_default": "no",
        "cancelled": "Cancelado.",
        "day_cleared": "Ok.",
        "date_prompt": "Fecha AAAA-MM-DD",
        "invalid_date": "Fecha inválida.",
        "menu": "Menú",
        "m1": "+tarea",
        "m2": "−tarea",
        "m3": "+nota",
        "m4": "−nota",
        "m5": "ayer",
        "m6": "hoy",
        "m7": "mañana",
        "m8": "fecha",
        "m0": "borrar",
        "ml": "idioma",
        "mq": "salir",
        "data": "Datos",
        "choice": ">",
        "bye": "¡Hasta luego!",
        "unknown": "No.",
        "lang_menu": "1 en  2 ru  3 es",
        "lang_set": "Idioma: español.",
        "yes_words": ("sí", "si", "s", "yes", "y"),
    },
}

lang = DEFAULT_LANG


def t(key: str) -> str:
    bundle = I18N.get(lang) or I18N[DEFAULT_LANG]
    value = bundle.get(key, I18N[DEFAULT_LANG].get(key, key))
    return value if isinstance(value, str) else key


def setup_console() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass
        try:
            os.system("")
        except Exception:
            pass


def clear() -> None:
    os.system("cls" if sys.platform == "win32" else "clear")


def pause(msg: str | None = None) -> None:
    input(msg if msg is not None else t("pause"))


def to_key(d: date) -> str:
    return d.isoformat()


def from_key(key: str) -> date:
    return date.fromisoformat(key)


def normalize_lang(value: object) -> str:
    if isinstance(value, str) and value.lower() in LANGS:
        return value.lower()
    return DEFAULT_LANG


def load_store() -> dict:
    try:
        if not DATA_PATH.exists():
            return {"days": {}, "lang": DEFAULT_LANG}
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"days": {}, "lang": DEFAULT_LANG}
        if "days" not in data or not isinstance(data["days"], dict):
            data["days"] = {}
        data["lang"] = normalize_lang(data.get("lang", DEFAULT_LANG))
        return data
    except Exception:
        return {"days": {}, "lang": DEFAULT_LANG}


def save_store(store: dict) -> None:
    store["lang"] = normalize_lang(store.get("lang", lang))
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(
        json.dumps(store, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def uid() -> str:
    return f"{int(time.time() * 1000):x}-{random.randrange(16**6):06x}"


def day_bucket(store: dict, key: str) -> dict:
    days = store.setdefault("days", {})
    if key not in days:
        days[key] = {"tasks": [], "notes": []}
    bucket = days[key]
    bucket.setdefault("tasks", [])
    bucket.setdefault("notes", [])
    return bucket


def format_title(key: str) -> str:
    today = date.today()
    d = from_key(key)
    parts = DATE_PARTS.get(lang) or DATE_PARTS[DEFAULT_LANG]
    if lang == "en":
        label = f"{parts['weekdays'][d.weekday()]}, {parts['months'][d.month]} {d.day}"
    else:
        label = f"{parts['weekdays'][d.weekday()]}, {d.day} {parts['months'][d.month]}"
    if d == today:
        return f"{t('today')} · {label}"
    if d == today - timedelta(days=1):
        return f"{t('yesterday')} · {label}"
    if d == today + timedelta(days=1):
        return f"{t('tomorrow')} · {label}"
    if lang == "en":
        return label
    return label[0].upper() + label[1:]


def nearest_half_hour() -> str:
    now = datetime.now().replace(second=0, microsecond=0)
    if now.minute < 30:
        now = now.replace(minute=30)
    else:
        now = now.replace(minute=0) + timedelta(hours=1)
    return now.strftime("%H:%M")


def normalize_time(raw: str) -> str | None:
    raw = raw.strip().replace(".", ":")
    m = TIME_RE.match(raw)
    if not m:
        return None
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def ask(prompt: str, default: str | None = None) -> str:
    if default is not None:
        line = input(f"{prompt} [{default}]: ").strip()
        return line or default
    return input(f"{prompt}: ").strip()


def print_header(current: str) -> None:
    title = "DAYFLOW"
    inner = f" {title} "
    width = max(len(inner), 12)
    top = "┌" + "─" * width + "┐"
    mid = "│" + inner.center(width) + "│"
    bot = "└" + "─" * width + "┘"
    print(top)
    print(mid)
    print(bot)
    print(f"{format_title(current)}\t{current}")
    print()


def task_lines(bucket: dict) -> list[str]:
    tasks = sorted(bucket["tasks"], key=lambda item: item.get("time", ""))
    if not tasks:
        return [f"{t('schedule')}: {t('empty')}"]
    lines = [f"{t('schedule')}:"]
    for i, task in enumerate(tasks, 1):
        title = task.get("title", "")
        if len(title) > 40:
            title = title[:37] + "..."
        lines.append(f" {i}. {task.get('time', '--:--')} {title}")
    return lines


def note_lines(bucket: dict) -> list[str]:
    notes = sorted(bucket["notes"], key=lambda item: item.get("created", 0), reverse=True)
    if not notes:
        return [f"{t('notes')}: {t('empty')}"]
    lines = [f"{t('notes')}:"]
    for i, note in enumerate(notes, 1):
        title = note.get("title") or t("untitled")
        body = (note.get("body") or "").replace("\n", " ")
        line = f"{title}: {body}" if body else title
        if len(line) > 44:
            line = line[:41] + "..."
        lines.append(f" {i}. {line}")
    return lines


def menu_lines() -> list[str]:
    return [
        f"1 {t('m1')}",
        f"2 {t('m2')}",
        "",
        f"3 {t('m3')}",
        f"4 {t('m4')}",
        "",
        f"5 {t('m5')}",
        f"6 {t('m6')}",
        f"7 {t('m7')}",
        "",
        f"8 {t('m8')}",
        f"9 {t('m0')}",
        "",
        f"l {t('ml')}",
        f"q {t('mq')}",
    ]


def content_lines(bucket: dict, left: list[str]) -> list[str]:
    """Plan beside task buttons; notes beside day-nav block."""
    plan = task_lines(bucket)
    notes = note_lines(bucket)
    day_row = next((i for i, line in enumerate(left) if line.startswith("5 ")), 6)
    right = [""] * max(len(left), day_row + len(notes), len(plan))
    for i, line in enumerate(plan):
        right[i] = line
    note_start = day_row
    if len(plan) > day_row:
        note_start = len(plan) + 1
        while len(right) < note_start + len(notes):
            right.append("")
    for i, line in enumerate(notes):
        idx = note_start + i
        while len(right) <= idx:
            right.append("")
        right[idx] = line
    return right


def show_screen(store: dict, current: str) -> None:
    clear()
    print_header(current)
    bucket = day_bucket(store, current)
    left = menu_lines()
    right = content_lines(bucket, left)
    left_w = max((len(line) for line in left), default=8) + 4
    rows = max(len(left), len(right))
    for i in range(rows):
        l = left[i] if i < len(left) else ""
        r = right[i] if i < len(right) else ""
        print(f"{l:<{left_w}}{r}")


def add_task(store: dict, current: str) -> None:
    time_s = normalize_time(ask(t("time_prompt"), nearest_half_hour()))
    if not time_s:
        print(t("invalid_time"))
        pause()
        return
    title = ask(t("what_to_do"))
    if not title:
        print(t("empty_title"))
        pause()
        return
    day_bucket(store, current)["tasks"].append(
        {"id": uid(), "time": time_s, "title": title, "done": False}
    )
    save_store(store)


def pick_task(bucket: dict) -> dict | None:
    tasks = sorted(bucket["tasks"], key=lambda item: item.get("time", ""))
    if not tasks:
        print(t("no_tasks"))
        pause()
        return None
    raw = ask(t("task_number"))
    if not raw.isdigit() or not (1 <= int(raw) <= len(tasks)):
        print(t("invalid_number"))
        pause()
        return None
    return tasks[int(raw) - 1]


def delete_task(store: dict, current: str) -> None:
    bucket = day_bucket(store, current)
    task = pick_task(bucket)
    if not task:
        return
    bucket["tasks"] = [item for item in bucket["tasks"] if item.get("id") != task.get("id")]
    save_store(store)


def add_note(store: dict, current: str) -> None:
    title = ask(t("note_title"), "")
    print(t("note_text"))
    lines: list[str] = []
    while True:
        line = input()
        if line == "" and lines:
            break
        if line == "" and not lines:
            print(t("need_line"))
            continue
        lines.append(line)
    body = "\n".join(lines).strip()
    if not body:
        print(t("empty_note"))
        pause()
        return
    day_bucket(store, current)["notes"].append(
        {
            "id": uid(),
            "title": title.strip(),
            "body": body,
            "created": int(time.time() * 1000),
        }
    )
    save_store(store)


def delete_note(store: dict, current: str) -> None:
    bucket = day_bucket(store, current)
    notes = sorted(bucket["notes"], key=lambda item: item.get("created", 0), reverse=True)
    if not notes:
        print(t("no_notes"))
        pause()
        return
    raw = ask(t("note_number"))
    if not raw.isdigit() or not (1 <= int(raw) <= len(notes)):
        print(t("invalid_number"))
        pause()
        return
    victim = notes[int(raw) - 1]
    bucket["notes"] = [item for item in bucket["notes"] if item.get("id") != victim.get("id")]
    save_store(store)


def clear_day(store: dict, current: str) -> None:
    ans = ask(t("clear_confirm"), t("clear_default"))
    yes_words = I18N[lang]["yes_words"]
    if ans.lower() not in yes_words:
        return
    store.setdefault("days", {})[current] = {"tasks": [], "notes": []}
    save_store(store)


def goto_date(current: str) -> str:
    raw = ask(t("date_prompt"), current)
    try:
        return to_key(from_key(raw))
    except ValueError:
        print(t("invalid_date"))
        pause()
        return current


def change_language(store: dict) -> None:
    global lang
    print(t("lang_menu"))
    choice = ask(t("choice"))
    mapping = {"1": "en", "2": "ru", "3": "es", "en": "en", "ru": "ru", "es": "es"}
    next_lang = mapping.get(choice.lower())
    if not next_lang:
        print(t("unknown"))
        pause()
        return
    lang = next_lang
    store["lang"] = lang
    save_store(store)


def main() -> int:
    global lang
    setup_console()
    store = load_store()
    lang = normalize_lang(store.get("lang", DEFAULT_LANG))
    store["lang"] = lang
    current = to_key(date.today())

    while True:
        show_screen(store, current)
        choice = ask(t("choice")).lower()

        if choice in ("q", "exit", "quit", "выход", "salir"):
            print(t("bye"))
            return 0
        if choice == "1":
            add_task(store, current)
        elif choice == "2":
            delete_task(store, current)
        elif choice == "3":
            add_note(store, current)
        elif choice == "4":
            delete_note(store, current)
        elif choice == "5":
            current = to_key(from_key(current) - timedelta(days=1))
        elif choice == "6":
            current = to_key(date.today())
        elif choice == "7":
            current = to_key(from_key(current) + timedelta(days=1))
        elif choice == "8":
            current = goto_date(current)
        elif choice == "9":
            clear_day(store, current)
        elif choice in ("l", "lang", "language", "idioma", "язык"):
            change_language(store)
        else:
            print(t("unknown"))
            pause()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print(f"\n{I18N.get(lang, I18N[DEFAULT_LANG])['bye']}")
        raise SystemExit(0)
