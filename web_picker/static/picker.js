document.addEventListener("DOMContentLoaded", () => {
  const tg = window.Telegram?.WebApp;

  // ===== Telegram WebApp bootstrapping =====
  if (tg) {
    tg.expand();
    tg.setHeaderColor?.("secondary_bg_color");
    if (tg.themeParams?.bg_color) document.body.style.backgroundColor = tg.themeParams.bg_color;
    if (tg.themeParams?.text_color) document.body.style.color = tg.themeParams.text_color;

    tg.BackButton?.show();
    tg.BackButton?.onClick(() => tg.close());

    // Показать нативную кнопку и связать её с submit()
    tg.MainButton.setText("Готово");
    tg.MainButton.show();
    tg.ready(); // сообщаем клиенту, что UI готов
  }

  // ===== DOM =====
  const input     = document.getElementById("dt");
  const hint      = document.getElementById("hint");
  const btnSubmit = document.getElementById("submit");
  const btnCancel = document.getElementById("cancel");

  // ===== helpers =====
  function roundUp(date, stepMin = 5) {
    const ms = date.getTime();
    const stepMs = stepMin * 60 * 1000;
    return new Date(Math.ceil(ms / stepMs) * stepMs);
  }
  const pad = n => (n < 10 ? "0" + n : "" + n);
  const toLocalInputValue = d =>
    `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;

  function updateHint() {
    if (!input.value) { hint.textContent = ""; return; }
    const chosen = new Date(input.value); // локальное
    const diffMs = chosen - new Date();
    const mins = Math.round(diffMs / 60000);
    if (mins < 0) {
      hint.textContent = `⛔ В прошлом: ${Math.abs(mins)} мин назад`;
      return;
    }
    const h = Math.floor(mins / 60), m = mins % 60;
    hint.textContent = `Через ${h ? h + " ч " : ""}${m} мин`;
  }

  function setDefault() {
    // ближайшие 15 минут
    const def = roundUp(new Date(Date.now() + 15 * 60 * 1000));
    input.value = toLocalInputValue(def);
    // min — чтобы нельзя было выбрать прошлое
    input.min = toLocalInputValue(roundUp(new Date(Date.now() + 60 * 1000)));
    updateHint();
  }

  // ===== пресеты (чипы) =====
  document.querySelectorAll(".chip").forEach((el) => {
    el.addEventListener("click", () => {
      const plus = el.dataset.plus;
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
    });
  });

  // ===== события =====
  input.addEventListener("input", updateHint);  // реагирует и на ввод с клавы, и на выбор из пикера
  input.addEventListener("change", updateHint);

  btnCancel.addEventListener("click", () => {
    if (tg?.close) tg.close();
    else window.close();
  });

  const submit = () => {
    if (!input.value) {
      hint.textContent = "Выберите дату и время";
      return;
    }

    const chosenLocal = new Date(input.value);
    if (chosenLocal <= new Date()) {
      const adj = roundUp(new Date(Date.now() + 60 * 1000));
      input.value = toLocalInputValue(adj);
      updateHint();
      return;
    }

    // Готовим payload
    const isoUtc = chosenLocal.toISOString(); // нормализуем в UTC
    const payload = {
      iso_utc: isoUtc,
      unix: Math.floor(chosenLocal.getTime() / 1000),
      local: input.value, // строка datetime-local как есть
      tz_offset_min: -chosenLocal.getTimezoneOffset(),
      step_min: 5,
    };

    try {
      if (tg?.sendData) {
        tg.sendData(JSON.stringify(payload));
        // на некоторых клиентах авто-закрытия нет — закроем явно
        setTimeout(() => tg?.close?.(), 50);
      } else {
        alert(JSON.stringify(payload, null, 2));
        window.close();
      }
    } catch (e) {
      console.error(e);
      alert("Ошибка: " + e);
    }
  };

  // клики
  btnSubmit.addEventListener("click", submit);
  // нативная кнопка Telegram
  tg?.MainButton?.onClick(submit);

  setDefault();
});