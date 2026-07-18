#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dayflow — console daily schedule and notes."""

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


def pause(msg: str = "Press Enter to continue…") -> None:
    input(msg)


def to_key(d: date) -> str:
    return d.isoformat()


def from_key(key: str) -> date:
    return date.fromisoformat(key)


def load_store() -> dict:
    try:
        if not DATA_PATH.exists():
            return {"days": {}}
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "days" not in data:
            return {"days": {}}
        return data
    except Exception:
        return {"days": {}}


def save_store(store: dict) -> None:
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
    label = d.strftime("%A, %B %d").replace(" 0", " ")
    if d == today:
        return f"Today · {label}"
    if d == today - timedelta(days=1):
        return f"Yesterday · {label}"
    if d == today + timedelta(days=1):
        return f"Tomorrow · {label}"
    return label


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
    print("=" * 52)
    print("  DAYFLOW")
    print(f"  {format_title(current)}")
    print(f"  {current}")
    print("=" * 52)


def print_tasks(bucket: dict) -> None:
    tasks = sorted(bucket["tasks"], key=lambda t: t.get("time", ""))
    print("\n  Schedule")
    print("  " + "-" * 40)
    if not tasks:
        print("  (empty)")
        return
    for i, task in enumerate(tasks, 1):
        mark = "[x]" if task.get("done") else "[ ]"
        print(f"  {i}. {mark} {task.get('time', '--:--')}  {task.get('title', '')}")


def print_notes(bucket: dict) -> None:
    notes = sorted(bucket["notes"], key=lambda n: n.get("created", 0), reverse=True)
    print("\n  Notes")
    print("  " + "-" * 40)
    if not notes:
        print("  (empty)")
        return
    for i, note in enumerate(notes, 1):
        title = note.get("title") or "Untitled"
        created = note.get("created")
        when = ""
        if created:
            when = datetime.fromtimestamp(created / 1000).strftime("%H:%M")
        body = (note.get("body") or "").replace("\n", " / ")
        if len(body) > 60:
            body = body[:57] + "..."
        print(f"  {i}. {title}" + (f"  ({when})" if when else ""))
        print(f"     {body}")


def show_day(store: dict, current: str) -> None:
    clear()
    print_header(current)
    bucket = day_bucket(store, current)
    print_tasks(bucket)
    print_notes(bucket)
    print()


def add_task(store: dict, current: str) -> None:
    time_s = normalize_time(ask("Time HH:MM", nearest_half_hour()))
    if not time_s:
        print("Invalid time format.")
        pause()
        return
    title = ask("What to do")
    if not title:
        print("Empty title.")
        pause()
        return
    day_bucket(store, current)["tasks"].append(
        {"id": uid(), "time": time_s, "title": title, "done": False}
    )
    save_store(store)
    print("Added.")
    pause()


def pick_task(bucket: dict) -> dict | None:
    tasks = sorted(bucket["tasks"], key=lambda t: t.get("time", ""))
    if not tasks:
        print("No tasks.")
        pause()
        return None
    print_tasks(bucket)
    raw = ask("Task number")
    if not raw.isdigit() or not (1 <= int(raw) <= len(tasks)):
        print("Invalid number.")
        pause()
        return None
    return tasks[int(raw) - 1]


def toggle_task(store: dict, current: str) -> None:
    bucket = day_bucket(store, current)
    task = pick_task(bucket)
    if not task:
        return
    task["done"] = not task.get("done", False)
    save_store(store)
    print("Done." if task["done"] else "Undone.")
    pause()


def delete_task(store: dict, current: str) -> None:
    bucket = day_bucket(store, current)
    task = pick_task(bucket)
    if not task:
        return
    bucket["tasks"] = [t for t in bucket["tasks"] if t.get("id") != task.get("id")]
    save_store(store)
    print("Deleted.")
    pause()


def add_note(store: dict, current: str) -> None:
    title = ask("Title (optional)", "")
    print("Note text (empty line to finish):")
    lines: list[str] = []
    while True:
        line = input()
        if line == "" and lines:
            break
        if line == "" and not lines:
            print("Need at least one line.")
            continue
        lines.append(line)
    body = "\n".join(lines).strip()
    if not body:
        print("Empty note.")
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
    print("Saved.")
    pause()


def delete_note(store: dict, current: str) -> None:
    bucket = day_bucket(store, current)
    notes = sorted(bucket["notes"], key=lambda n: n.get("created", 0), reverse=True)
    if not notes:
        print("No notes.")
        pause()
        return
    print_notes(bucket)
    raw = ask("Note number")
    if not raw.isdigit() or not (1 <= int(raw) <= len(notes)):
        print("Invalid number.")
        pause()
        return
    victim = notes[int(raw) - 1]
    bucket["notes"] = [n for n in bucket["notes"] if n.get("id") != victim.get("id")]
    save_store(store)
    print("Deleted.")
    pause()


def clear_day(store: dict, current: str) -> None:
    ans = ask("Delete all tasks and notes for this day? (yes/no)", "no")
    if ans.lower() not in ("yes", "y"):
        print("Cancelled.")
        pause()
        return
    store.setdefault("days", {})[current] = {"tasks": [], "notes": []}
    save_store(store)
    print("Day cleared.")
    pause()


def goto_date(current: str) -> str:
    raw = ask("Date YYYY-MM-DD", current)
    try:
        return to_key(from_key(raw))
    except ValueError:
        print("Invalid date.")
        pause()
        return current


def main_menu(current: str) -> None:
    print("  Menu")
    print("  " + "-" * 40)
    print("  1  Add task")
    print("  2  Toggle task done")
    print("  3  Delete task")
    print("  4  Add note")
    print("  5  Delete note")
    print("  6  Yesterday")
    print("  7  Tomorrow")
    print("  8  Today")
    print("  9  Go to date")
    print("  0  Clear day")
    print("  q  Quit")
    print(f"\n  Data: {DATA_PATH}")


def main() -> int:
    setup_console()
    store = load_store()
    current = to_key(date.today())

    while True:
        show_day(store, current)
        main_menu(current)
        choice = ask("\nChoice").lower()

        if choice in ("q", "exit", "quit"):
            print("Bye!")
            return 0
        if choice == "1":
            add_task(store, current)
        elif choice == "2":
            toggle_task(store, current)
        elif choice == "3":
            delete_task(store, current)
        elif choice == "4":
            add_note(store, current)
        elif choice == "5":
            delete_note(store, current)
        elif choice == "6":
            current = to_key(from_key(current) - timedelta(days=1))
        elif choice == "7":
            current = to_key(from_key(current) + timedelta(days=1))
        elif choice == "8":
            current = to_key(date.today())
        elif choice == "9":
            current = goto_date(current)
        elif choice == "0":
            clear_day(store, current)
        else:
            print("Unknown option.")
            pause()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nBye!")
        raise SystemExit(0)
