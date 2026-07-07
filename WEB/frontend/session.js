// Простейшая "сессия" в localStorage (в проекте нет JWT/токенов,
// поэтому храним данные пользователя, которые вернул /users/login).
const Session = {
  KEY: "azs_user",

  save(user) {
    localStorage.setItem(this.KEY, JSON.stringify(user));
  },
  get() {
    const raw = localStorage.getItem(this.KEY);
    return raw ? JSON.parse(raw) : null;
  },
  clear() {
    localStorage.removeItem(this.KEY);
  },
  isLoggedIn() {
    return !!this.get();
  }
};
