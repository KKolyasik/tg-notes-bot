document.addEventListener("DOMContentLoaded", () => {
  const tg = window.Telegram?.WebApp;

  // --- Telegram bootstrap ---
  if (tg) {
    tg.expand();
    tg.setHeaderColor?.("secondary_bg_color");
    if (tg.themeParams?.bg_color) document.body.style.backgroundColor = tg.themeParams.bg_color;
    if (tg.themeParams?.text_color) document.body.style.color = tg.themeParams.text_color;

    tg.BackButton?.show();
    tg.BackButton?.onClick(() => tg.close());

    tg.MainButton.setText("Готово");
    tg.MainButton.show();
    tg.ready?.();
  }

  // --- DOM ---
  const input = document.getElementById("dt");
  const hint  = document.getElementById("hint");
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
    if (mins < 0) { hint.textContent = `⛔ В прошлом: ${Math.abs(mins)} мин назад`; return; }
    const h = Math.floor(mins / 60), m = mins % 60;
    hint.textContent = `Через ${h ? h + " ч " : ""}${m} мин`;
  }

  function setDefault() {
    const def = roundUp(new Date(Date.now() + 15 * 60 * 1000));
    input.value = toLocalInputValue(def);
    input.min   = toLocalInputValue(roundUp(new Date(Date.now() + 60 * 1000)));
    updateHint();
  }

  // Пресеты
  document.querySelectorAll(".chip").forEach((el) => {
    el.addEventListener("click", () => {
      const plus = el.dataset.plus;
      const preset = el.dataset.preset;
      let dt = input.value ? new Date(input.value) : new Date();

      if (plus) dt = new Date(dt.getTime() + Number(plus) * 60000);
      else if (preset === "tomorrow_9") {
        dt = new Date();
        dt.setDate(dt.getDate() + 1);
        dt.setHours(9, 0, 0, 0);
      }
      dt = roundUp(dt);
      input.value = toLocalInputValue(dt);
      updateHint();
    });
  });

  input.addEventListener("input", updateHint);
  input.addEventListener("change", updateHint);

  btnCancel.addEventListener("click", () => tg?.close?.());

  // --- вариант B: отправка на backend + answerWebAppQuery ---
  async function submit() {
    if (!tg) {
      alert("Откройте через Telegram.");
      return;
    }
    // query_id есть только при старте из inline-кнопки/меню
    const queryId = tg.initDataUnsafe?.query_id;
    if (!queryId) {
      tg.showAlert?.("Эта страница открыта не через inline WebApp.");
      return;
    }
    if (!input.value) {
      hint.textContent = "Выберите дату и время";
      return;
    }

    const chosenLocal = new Date(input.value);
    if (Number.isNaN(chosenLocal.getTime())) {
      hint.textContent = "Некорректная дата";
      return;
    }
    if (chosenLocal <= new Date()) {
      const adj = roundUp(new Date(Date.now() + 60 * 1000));
      input.value = toLocalInputValue(adj);
      updateHint();
      return;
    }

    const payload = {
      iso_utc: chosenLocal.toISOString(),
      local: input.value,                           // строка из <input>
      tz_offset_min: -chosenLocal.getTimezoneOffset(),
      step_min: 5,
      query_id: queryId,                            // обязательно
      init_data: tg.initData,                       // чтобы сервер мог валидировать HMAC (рекомендуется)
      // при желании добавь свои поля, например note_id из query-параметра
      // note_id: new URLSearchParams(location.search).get("note_id")
    };

    // блокируем повторные клики
    btnSubmit.disabled = true;
    tg.MainButton?.showProgress?.();

    try {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 8000);

      const res = await fetch("/tma/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Init-Data": tg.initData, // дублируем заголовком, чтобы не вытаскивать из body
        },
        body: JSON.stringify(payload),
        signal: ctrl.signal,
      });
      clearTimeout(timer);

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        tg.showAlert?.("Ошибка отправки: " + (text || res.status));
        btnSubmit.disabled = false;
        tg.MainButton?.hideProgress?.();
        return;
      }

      // сервер сам вызовет answerWebAppQuery → в чате появится сообщение
      tg.close();
    } catch (e) {
      tg.showAlert?.("Сеть недоступна. Повторите позже.");
      btnSubmit.disabled = false;
      tg.MainButton?.hideProgress?.();
    }
  }

  btnSubmit.addEventListener("click", submit);
  tg?.MainButton?.onClick(submit);

  setDefault();
});