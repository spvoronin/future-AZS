const API_BASE = "https://api.smartaf.ru"; // Твой бэкенд FastAPI

export const Api = {
async _request(method, path, body) {
    let token = null;
    const opts = { method, headers: {} };
    const userData = localStorage.getItem("azs_user")
    if (userData) {
      try {
        const parsed = JSON.parse(userData);
        token = parsed.token;
      } catch (e) {
        console.error("Ошибка парсинга azs_user в API:", e);
      }
    }
    if (token) {
      opts.headers["Authorization"] = `Bearer ${token}`;
    }

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
      if (res.status === 401) {
        localStorage.removeItem("azs_user");
      }
      const message = (data && data.message) || `Ошибка запроса (${res.status})`;
      throw new Error(message);
    }
    return data;
  },

  get(path) { return this._request("GET", path); },
  post(path, body) { return this._request("POST", path, body); },

  // --- Пользователи ---
  async login(email, password_hash) {
    const data = await this.post("/users/login", { email, password_hash });
    if (data && data.token) {
        localStorage.setItem("azs_user", JSON.stringify(data));
    }
    return data;
  },
  getAllUsers() {
    return this.get("/users");
  },
  register(formData){
    return this.post("/users/register", formData)
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
  },

  postRele(pump_id) {
    return this.post(`/sensors/pumps/${pump_id}`)
  }
};