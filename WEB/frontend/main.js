// ---------- Состояние страницы ----------
const state = {
  stationId: null,
  prices: [], // [{fuel_type, prices_per_liter}]
  pumps: [], // [{pump_number, status, is_active, id}]
  selectedFuel: null,
  selectedPump: null,
  selectedVolume: 20
};

const el = (id) => document.getElementById(id);

// ---------- Инициализация ----------
document.addEventListener("DOMContentLoaded", async () => {
  updateLoginButton();
  await loadStationAndData();
  bindLoginModal();
  bindPurchasePanel();
});

async function loadStationAndData() {
  try {
    const stations = await Api.getStations();
    if (!Array.isArray(stations) || stations.length === 0) {
      el("stationBadge").textContent = "Нет станций";
      return;
    }
    // Берём первую станцию из списка. При желании можно заменить
    // на выбор пользователем / поиск по геолокации.
    const station = stations[0];
    state.stationId = station.id;
    el("stationBadge").textContent = `АЗС №${station.id} — ${station.adress}`;

    await Promise.all([loadPrices(), loadPumps()]);
  } catch (err) {
    console.error(err);
    el("stationBadge").textContent = "Ошибка загрузки станции";
  }
}

async function loadPrices() {
  const row = el("pricesRow");
  try {
    const data = await Api.getPrices(state.stationId);
    if (!Array.isArray(data)) {
      row.innerHTML = `<div class="empty-note">${data.message || "Цены не найдены"}</div>`;
      return;
    }
    state.prices = data;
    row.innerHTML = "";
    data.forEach((p, idx) => {
      const div = document.createElement("div");
      div.className = "price-card" + (idx === 0 ? " selected" : "");
      div.dataset.fuel = p.fuel_type;
      div.innerHTML = `<div class="fuel-name">${p.fuel_type}</div><div class="fuel-price">${p.prices_per_liter} ₽/л</div>`;
      div.addEventListener("click", () => selectFuel(p.fuel_type));
      row.appendChild(div);
    });
    if (data.length) selectFuel(data[0].fuel_type);
  } catch (err) {
    row.innerHTML = `<div class="empty-note">Не удалось загрузить цены</div>`;
  }
}

function selectFuel(fuelType) {
  state.selectedFuel = fuelType;
  document.querySelectorAll(".price-card").forEach((c) => {
    c.classList.toggle("selected", c.dataset.fuel === fuelType);
  });
  updateSummary();
}

async function loadPumps() {
  const row = el("pumpsRow");
  try {
    const data = await Api.getStationPumps(state.stationId);
    if (!Array.isArray(data)) {
      row.innerHTML = `<div class="empty-note">${data.message || "Колонки не найдены"}</div>`;
      return;
    }
    state.pumps = data;
    row.innerHTML = "";
    data.forEach((p) => {
      const free = p.is_active && p.status === "idle";
      const div = document.createElement("div");
      div.className = "pump-card " + (free ? "free" : p.is_active ? "busy" : "disabled");
      div.innerHTML = `<div class="pump-title">Колонка ${p.pump_number}</div><div class="pump-status">${pumpStatusLabel(p, free)}</div>`;
      if (free) {
        div.addEventListener("click", () => selectPump(p, div));
      }
      row.appendChild(div);
    });
  } catch (err) {
    row.innerHTML = `<div class="empty-note">Не удалось загрузить колонки</div>`;
  }
}

function pumpStatusLabel(p, free) {
  if (!p.is_active) return "недоступна";
  if (p.status === "idle") return "свободна";
  if (p.status === "dispensing") return "идёт налив";
  return "сбой";
}

function selectPump(pump, cardEl) {
  state.selectedPump = pump;
  document.querySelectorAll(".pump-card").forEach((c) => c.classList.remove("selected"));
  cardEl.classList.add("selected");
  el("yourStationInfo").textContent = `Колонка ${pump.pump_number} выбрана`;
}

// ---------- Панель покупки ----------
function bindPurchasePanel() {
  document.querySelectorAll(".volume-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".volume-btn").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      el("customVol").value = "";
      state.selectedVolume = parseFloat(btn.dataset.vol);
      updateSummary();
    });
  });

  el("customVol").addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val) && val > 0) {
      document.querySelectorAll(".volume-btn").forEach((b) => b.classList.remove("selected"));
      state.selectedVolume = val;
      updateSummary();
    }
  });

  el("payBtn").addEventListener("click", handlePay);
  updateSummary();
}

function updateSummary() {
  const priceEntry = state.prices.find((p) => p.fuel_type === state.selectedFuel);
  const pricePerLiter = priceEntry ? priceEntry.prices_per_liter : 0;
  const total = (pricePerLiter * state.selectedVolume).toFixed(2);
  el("sumVolume").textContent = `${state.selectedVolume} л`;
  el("sumPrice").textContent = priceEntry ? `${pricePerLiter} ₽/л` : "—";
  el("sumTotal").textContent = `${total} ₽`;
}

async function handlePay() {
  el("payError").textContent = "";
  const user = Session.get();
  if (!user) {
    el("payError").textContent = "Сначала войдите в аккаунт";
    openLogin();
    return;
  }
  if (!state.selectedPump) {
    el("payError").textContent = "Выберите свободную колонку";
    return;
  }
  if (!state.selectedFuel) {
    el("payError").textContent = "Выберите вид топлива";
    return;
  }

  try {
    const payload = {
      user_id: user.id,
      pump_id: state.selectedPump.id,
      fuel_type: state.selectedFuel,
      requested_liters: state.selectedVolume
    };
    const res = await Api.createTransaction(payload);
    if (res.status === "error") {
      el("payError").textContent = res.message;
      return;
    }
    alert(
      `Заказ №${res.transaction_id} оформлен!\nК оплате: ${res.total_cost_rub} ₽\nНалив запущен на выбранной колонке.`
    );
    await loadPumps();
  } catch (err) {
    el("payError").textContent = err.message || "Ошибка оформления заказа";
  }
}

// ---------- Логин ----------
function updateLoginButton() {
  const user = Session.get();
  const btn = el("loginBtn");
  if (user) {
    btn.textContent = user.first_name || "Профиль";
    btn.onclick = () => (window.location.href = "profile.html");
  } else {
    btn.textContent = "Вход";
    btn.onclick = openLogin;
  }
}

function openLogin() {
  el("loginOverlay").classList.remove("hidden");
  el("loginError").textContent = "";
}

function closeLogin() {
  el("loginOverlay").classList.add("hidden");
}

function bindLoginModal() {
  el("loginBtn").addEventListener("click", openLogin);
  el("loginCancel").addEventListener("click", closeLogin);

  el("loginSubmit").addEventListener("click", async () => {
    const email = el("loginEmail").value.trim();
    const password = el("loginPassword").value;
    const errEl = el("loginError");
    errEl.textContent = "";

    if (!email || !password) {
      errEl.textContent = "Заполните оба поля";
      return;
    }

    try {
      // ВАЖНО: бэкенд сравнивает password_hash "как есть", без реального
      // хэширования, поэтому здесь просто передаём введённый пароль.
      const res = await Api.login(email, password);
      if (res.code === 401 || res.message === "Unauthorized") {
        errEl.textContent = "Неверный email или пароль";
        return;
      }
      if (res.status === "error") {
        errEl.textContent = res.message;
        return;
      }

      // /users/login не возвращает id пользователя, поэтому подтягиваем
      // его из общего списка пользователей по email.
      let userId = null;
      try {
        const allUsers = await Api.getAllUsers();
        const match = Array.isArray(allUsers) ? allUsers.find((u) => u.email === email) : null;
        if (match) userId = match.id;
      } catch (e) {
        console.warn("Не удалось получить id пользователя", e);
      }

      Session.save({ ...res, id: userId });
      closeLogin();
      updateLoginButton();
    } catch (err) {
      errEl.textContent = err.message || "Ошибка входа";
    }
  });
}
