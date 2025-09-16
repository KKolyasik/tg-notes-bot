(function () {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.expand();
    if (tg.themeParams?.bg_color) document.body.style.backgroundColor = tg.themeParams.bg_color;
    if (tg.themeParams?.text_color) document.body.style.color = tg.themeParams.text_color;
    if (tg.setHeaderColor) tg.setHeaderColor("secondary_bg_color");
    if (tg.BackButton) {
      tg.BackButton.show();
      tg.BackButton.onClick(() => tg.close());
    }
  }

  const input = document.getElementById("dt");
  const hint = document.getElementById("hint");
  const btnSubmit = document.getElementById("submit");
  const btnCancel = document.getElementById("cancel");

  // округление вверх к шагу (5 минут)
  function roundUp(date, stepMin = 5) {
    const ms = date.getTime();
    const stepMs = stepMin * 60 * 1000;
    return new Date(Math.ceil(ms / stepMs) * stepMs);
  }

  function pad(n) { return n < 10 ? "0" + n : "" + n; }

  function toLocalInputValue(date) {
    const y = date.getFullYear();
    const m = pad(date.getMonth() + 1);
    const d = pad(date.getDate());
    const h = pad(date.getHours());
    const min = pad(date.getMinutes());
    return `${y}-${m}-${d}T${h}:${min}`;
  }

  function setDefault() {
    const now = new Date();
    const def = roundUp(new Date(now.getTime() + 15 * 60 * 1000));
    input.value = toLocalInputValue(def);
    updateHint();
  }

  function updateHint() {
    const val = input.value;
    if (!val) { hint.textContent = ""; return; }
    const chosen = new Date(val);
    const now = new Date();
    const diffMs = chosen - now;
    const mins = Math.round(diffMs / 60000);
    if (mins < 0) {
      hint.textContent = `⛔ В прошлом: ${Math.abs(mins)} мин назад`; return;
    }
    const hours = Math.floor(mins / 60);
    const m = mins % 60;
    hint.textContent = `Через ${hours ? hours + " ч " : ""}${m} мин`;
  }

  // Пресеты
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

  input.addEventListener("change", updateHint);

  btnCancel.addEventListener("click", () => {
    if (tg?.close) tg.close();
    else window.close();
  });

  btnSubmit.addEventListener("click", () => {
    const value = input.value; // локальное время без таймзоны
    if (!value) {
      hint.textContent = "Выберите дату и время";
      return;
    }
    const chosenLocal = new Date(value);
    const now = new Date();
    // В прошлое нельзя
    if (chosenLocal.getTime() <= now.getTime()) {
      const adj = roundUp(new Date(now.getTime() + 60 * 1000));
      input.value = toLocalInputValue(adj);
      updateHint();
      return;
    }

    // Собираем полезные поля
    const iso = new Date(value).toISOString(); // UTC ISO
    const tzOffsetMin = -new Date(value).getTimezoneOffset(); // для удобства (+180 для Europe/Helsinki летом)

    const payload = {
      iso_utc: iso,
      unix: Math.floor(new Date(value).getTime() / 1000),
      local: value,
      tz_offset_min: tzOffsetMin,
      step_min: 5,
    };

    if (tg?.sendData) {
      tg.sendData(JSON.stringify(payload));
      // Telegram сам закроет WebApp после отправки
    } else {
      alert(JSON.stringify(payload, null, 2));
    }
  });

  setDefault();
})();
