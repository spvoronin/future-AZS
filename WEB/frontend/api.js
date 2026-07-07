// Тонкая обёртка над fetch для общения с бэкендом.
const Api = {
  async _request(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(window.APP_CONFIG.API_BASE + path, opts);
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

  get(path) {
    return this._request("GET", path);
  },
  post(path, body) {
    return this._request("POST", path, body);
  },
  put(path, body) {
    return this._request("PUT", path, body);
  },
  del(path) {
    return this._request("DELETE", path);
  },

  // --- users ---
  login(email, password_hash) {
    return this.post("/users/login", { email, password_hash });
  },
  getAllUsers() {
    return this.get("/users");
  },

  // --- stations ---
  getStations() {
    return this.get("/stations");
  },
  getStation(id) {
    return this.get(`/stations/${id}`);
  },
  getStationPumps(stationId) {
    return this.get(`/stations/${stationId}/pumps`);
  },

  // --- prices ---
  getPrices(stationId) {
    return this.get(`/prices/${stationId}`);
  },

  // --- transactions ---
  createTransaction(payload) {
    return this.post("/transactions", payload);
  }
};
