(() => {
  const STORAGE_KEY = "dayflow.v1";
  const THEME_KEY = "dayflow.theme";

  const dateTitle = document.getElementById("dateTitle");
  const datePicker = document.getElementById("datePicker");
  const prevDay = document.getElementById("prevDay");
  const nextDay = document.getElementById("nextDay");
  const todayBtn = document.getElementById("todayBtn");
  const themeToggle = document.getElementById("themeToggle");
  const taskForm = document.getElementById("taskForm");
  const taskTime = document.getElementById("taskTime");
  const taskTitle = document.getElementById("taskTitle");
  const taskList = document.getElementById("taskList");
  const taskEmpty = document.getElementById("taskEmpty");
  const noteForm = document.getElementById("noteForm");
  const noteTitle = document.getElementById("noteTitle");
  const noteBody = document.getElementById("noteBody");
  const noteList = document.getElementById("noteList");
  const noteEmpty = document.getElementById("noteEmpty");
  const clearDay = document.getElementById("clearDay");

  /** @type {{ days: Record<string, { tasks: Array, notes: Array }> }} */
  let store = load();
  let currentDate = toKey(new Date());

  function getTheme() {
    return document.documentElement.getAttribute("data-theme") === "light"
      ? "light"
      : "dark";
  }

  function applyTheme(theme) {
    const next = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(THEME_KEY, next);
    themeToggle.textContent = next === "dark" ? "☀" : "☾";
    themeToggle.setAttribute(
      "aria-label",
      next === "dark" ? "Включить светлую тему" : "Включить тёмную тему"
    );
    themeToggle.title = themeToggle.getAttribute("aria-label");
  }

  applyTheme(localStorage.getItem(THEME_KEY) === "light" ? "light" : "dark");

  themeToggle.addEventListener("click", () => {
    applyTheme(getTheme() === "dark" ? "light" : "dark");
  });

  function toKey(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  function fromKey(key) {
    const [y, m, d] = key.split("-").map(Number);
    return new Date(y, m - 1, d);
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { days: {} };
      const data = JSON.parse(raw);
      if (!data || typeof data !== "object" || !data.days) return { days: {} };
      return data;
    } catch {
      return { days: {} };
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  }

  function day() {
    if (!store.days[currentDate]) {
      store.days[currentDate] = { tasks: [], notes: [] };
    }
    return store.days[currentDate];
  }

  function uid() {
    return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  }

  function formatTitle(key) {
    const today = toKey(new Date());
    const d = fromKey(key);
    const label = d.toLocaleDateString("ru-RU", {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
    if (key === today) return `Сегодня · ${label}`;
    const y = new Date();
    y.setDate(y.getDate() - 1);
    if (key === toKey(y)) return `Вчера · ${label}`;
    const t = new Date();
    t.setDate(t.getDate() + 1);
    if (key === toKey(t)) return `Завтра · ${label}`;
    return label.charAt(0).toUpperCase() + label.slice(1);
  }

  function shiftDay(delta) {
    const d = fromKey(currentDate);
    d.setDate(d.getDate() + delta);
    currentDate = toKey(d);
    render();
  }

  function renderHeader() {
    datePicker.value = currentDate;
    dateTitle.textContent = formatTitle(currentDate);
  }

  function renderTasks() {
    const { tasks } = day();
    const sorted = [...tasks].sort((a, b) => a.time.localeCompare(b.time));
    taskList.innerHTML = "";
    taskEmpty.hidden = sorted.length > 0;

    for (const task of sorted) {
      const li = document.createElement("li");
      li.className = `item${task.done ? " done" : ""}`;
      li.innerHTML = `
        <div class="time">${escapeHtml(task.time)}</div>
        <div>
          <div class="title">${escapeHtml(task.title)}</div>
        </div>
        <div class="actions">
          <button type="button" data-act="toggle" data-id="${task.id}">${task.done ? "↩" : "✓"}</button>
          <button type="button" class="del" data-act="del" data-id="${task.id}">✕</button>
        </div>
      `;
      taskList.appendChild(li);
    }
  }

  function renderNotes() {
    const { notes } = day();
    const sorted = [...notes].sort((a, b) => b.created - a.created);
    noteList.innerHTML = "";
    noteEmpty.hidden = sorted.length > 0;

    for (const note of sorted) {
      const when = new Date(note.created).toLocaleTimeString("ru-RU", {
        hour: "2-digit",
        minute: "2-digit",
      });
      const li = document.createElement("li");
      li.className = "item";
      li.innerHTML = `
        <div>
          <div class="title">${escapeHtml(note.title || "Без названия")}</div>
          <div class="meta">${when}</div>
          <div class="meta" style="margin-top:8px;white-space:pre-wrap;color:inherit">${escapeHtml(note.body)}</div>
        </div>
        <div class="actions">
          <button type="button" class="del" data-act="del-note" data-id="${note.id}">✕</button>
        </div>
      `;
      noteList.appendChild(li);
    }
  }

  function render() {
    renderHeader();
    renderTasks();
    renderNotes();
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });
      document.querySelectorAll(".panel").forEach((panel) => {
        const on = panel.id === `panel-${tab.dataset.tab}`;
        panel.classList.toggle("active", on);
        panel.hidden = !on;
      });
    });
  });

  prevDay.addEventListener("click", () => shiftDay(-1));
  nextDay.addEventListener("click", () => shiftDay(1));
  todayBtn.addEventListener("click", () => {
    currentDate = toKey(new Date());
    render();
  });
  datePicker.addEventListener("change", () => {
    if (datePicker.value) {
      currentDate = datePicker.value;
      render();
    }
  });

  taskForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = taskTitle.value.trim();
    const time = taskTime.value;
    if (!title || !time) return;
    day().tasks.push({ id: uid(), time, title, done: false });
    save();
    taskTitle.value = "";
    renderTasks();
    taskTitle.focus();
  });

  taskList.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-act]");
    if (!btn) return;
    const { act, id } = btn.dataset;
    const tasks = day().tasks;
    const idx = tasks.findIndex((t) => t.id === id);
    if (idx < 0) return;
    if (act === "toggle") tasks[idx].done = !tasks[idx].done;
    if (act === "del") tasks.splice(idx, 1);
    save();
    renderTasks();
  });

  noteForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const body = noteBody.value.trim();
    if (!body) return;
    day().notes.push({
      id: uid(),
      title: noteTitle.value.trim(),
      body,
      created: Date.now(),
    });
    save();
    noteTitle.value = "";
    noteBody.value = "";
    renderNotes();
  });

  noteList.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-act='del-note']");
    if (!btn) return;
    day().notes = day().notes.filter((n) => n.id !== btn.dataset.id);
    save();
    renderNotes();
  });

  clearDay.addEventListener("click", () => {
    if (!confirm("Удалить все задачи и заметки за этот день?")) return;
    store.days[currentDate] = { tasks: [], notes: [] };
    save();
    render();
  });

  // Default time: nearest next half-hour
  const now = new Date();
  now.setMinutes(now.getMinutes() < 30 ? 30 : 60, 0, 0);
  taskTime.value = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;

  render();
})();
