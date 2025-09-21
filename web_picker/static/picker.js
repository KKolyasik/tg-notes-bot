document.addEventListener("DOMContentLoaded", () => {
  const tg = window.Telegram?.WebApp;

  // --- тема Telegram → CSS-переменные ---
  function applyTheme(p) {
    const root = document.documentElement;
    const set = (name, val) => val && root.style.setProperty(name, val);
    set('--tg-theme-bg-color', p.bg_color);
    set('--tg-theme-text-color', p.text_color);
    set('--tg-theme-secondary-bg-color', p.secondary_bg_color);
    set('--tg-theme-hint-color', p.hint_color);
    set('--tg-theme-link-color', p.link_color);
    set('--tg-theme-button-color', p.button_color);
    set('--tg-theme-button-text-color', p.button_text_color);

    if (p.bg_color) {
      const hex = p.bg_color.replace('#', '');
      const r = parseInt(hex.slice(0,2),16);
      const g = parseInt(hex.slice(2,4),16);
      const b = parseInt(hex.slice(4,6),16);
      const isDark = (0.2126*r + 0.7152*g + 0.0722*b) < 128;
      root.style.setProperty('--tg-color-scheme', isDark ? 'dark' : 'light');
    }
  }

  // --- Telegram bootstrap ---
  if (tg) {
    tg.expand();
    tg.setHeaderColor?.("secondary_bg_color");
    applyTheme(tg.themeParams || {});
    tg.onEvent?.("themeChanged", () => applyTheme(tg.themeParams || {}));
    tg.BackButton?.show();
    tg.BackButton?.onClick(() => tg.close());
    tg.MainButton?.hide?.(); // убираем системную нижнюю кнопку
    tg.ready?.();
  }

  // --- DOM ---
  const input     = document.getElementById("dt");
  const hint      = document.getElementById("hint");
  const btnSubmit = document.getElementById("submit");
  const btnCancel = document.getElementById("cancel");

  // --- helpers ---
  function roundUp(date, stepMin = 5) {
    const stepMs = stepMin * 60 * 1000;
    return new Date(Math.ceil(date.getTime() / stepMs) * stepMs);
  }
  const pad = n => (n < 10 ? "0" + n : "" + n);
  const toLocalInputValue = d =>
    `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;

  function updateHint() {
    if (!input.value) { hint.textContent = ""; return; }
    const chosen = new Date(input.value);
    const mins = Math.round((chosen - new Date()) / 60000);
    if (Number.isNaN(mins)) { hint.textContent = "Некорректная дата"; return; }
    if (mins < 0) { hint.textContent = `⛔ В прошлом: ${Math.abs(mins)} мин назад`; return; }
    const h = Math.floor(mins / 60), m = mins % 60;
    hint.textContent = `Через ${h ? h + " ч " : ""}${m} мин`;
  }

  function setDefault() {
    const now = new Date();
    const def = roundUp(new Date(now.getTime() + 15 * 60 * 1000));
    const min = roundUp(new Date(now.getTime() + 2  * 60 * 1000));
    input.value = toLocalInputValue(def);
    input.min   = toLocalInputValue(min);
    updateHint();
    toggleSubmit();
  }

  function toggleSubmit() {
    btnSubmit.disabled = !input.value;
  }

  // пресеты
  document.querySelectorAll(".chip").forEach((el) => {
    el.addEventListener("click", () => {
      const plus   = el.dataset.plus;
      const preset = el.dataset.preset;
      let dt = input.value ? new Date(input.value) : new Date();

      if (plus) {
        dt = new Date(dt.getTime() + Number(plus) * 60000);
      } else if (preset === "tomorrow_9") {
        dt = new Date();
        dt.setDate(dt.getDate() + 1);
        dt.setHours(9, 0, 0, 0);
      }
      dt = roundUp(dt);
      input.value = toLocalInputValue(dt);
      updateHint();
      toggleSubmit();
    });
  });

  input.addEventListener("input", () => { updateHint(); toggleSubmit(); });
  input.addEventListener("change", () => { updateHint(); toggleSubmit(); });

  btnCancel.addEventListener("click", () => tg?.close?.());

  // --- отправка ---
  async function submit() {
    if (!tg) { alert("Откройте через Telegram."); return; }

    const queryId = tg.initDataUnsafe?.query_id;
    if (!queryId) {
      tg.showAlert?.("Эта страница открыта не через inline WebApp.");
      return;
    }
    if (!input.value) { hint.textContent = "Выберите дату и время"; return; }

    const chosenLocal = new Date(input.value);
    if (Number.isNaN(chosenLocal.getTime())) { hint.textContent = "Некорректная дата"; return; }
    if (chosenLocal <= new Date()) {
      const adj = roundUp(new Date(Date.now() + 60 * 1000));
      input.value = toLocalInputValue(adj);
      updateHint();
      return;
    }

    const payload = {
      iso_utc: chosenLocal.toISOString(),
      local: input.value,
      tz_offset_min: -chosenLocal.getTimezoneOffset(),
      step_min: 5,
      query_id: queryId,
      init_data: tg.initData, // для валидации на сервере
    };

    btnSubmit.disabled = true;
    const oldText = btnSubmit.textContent;
    btnSubmit.textContent = "Отправка…";

    try {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 8000);

      const res = await fetch("/tma/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Init-Data": tg.initData,
        },
        body: JSON.stringify(payload),
        signal: ctrl.signal,
      });
      clearTimeout(timer);

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        tg.showAlert?.("Ошибка отправки: " + (text || res.status));
        btnSubmit.disabled = false;
        btnSubmit.textContent = oldText;
        return;
      }

      // сервер вызывает answerWebAppQuery → сообщение в чате; закрываем окно
      tg.close();
    } catch (e) {
      tg.showAlert?.("Сеть недоступна. Повторите позже.");
      btnSubmit.disabled = false;
      btnSubmit.textContent = oldText;
    }
  }

  btnSubmit.addEventListener("click", submit);

  setDefault();
});