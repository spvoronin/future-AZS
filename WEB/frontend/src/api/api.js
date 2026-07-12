const API_BASE = "api.smartaf.ru"; // Твой бэкенд FastAPI

export const Api = {
  async _request(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(API_BASE + path, opts);
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      /* пустой ответ */
    }
    if (!res.ok) {
      const message = (data && data.message) || `Ошибка запроса (${res.status})`;
      throw new Error(message);
    }
    return data;
  },

  get(path) { return this._request("GET", path); },
  post(path, body) { return this._request("POST", path, body); },

  // --- Пользователи ---
  login(email, password_hash) {
    return this.post("/users/login", { email, password_hash });
  },
  getAllUsers() {
    return this.get("/users");
  },

  // --- Станции и Колонки ---
  getStations() {
    return this.get("/stations");
  },
  getStationPumps(stationId) {
    return this.get(`/stations/${stationId}/pumps`);
  },

  // --- Цены ---
  getPrices(stationId) {
    return this.get(`/prices/${stationId}`);
  },

  // --- Транзакции ---
  createTransaction(payload) {
    return this.post("/transactions", payload);
  },

  // --- Датчики (Новое) ---
  getSensors() {
    return this.get("/sensors");
  }
};