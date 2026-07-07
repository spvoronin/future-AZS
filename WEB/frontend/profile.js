const el = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  const user = Session.get();

  if (!user) {
    // Не авторизован — отправляем на главную, чтобы залогиниться
    el("profileName").textContent = "Вы не вошли в аккаунт";
    el("userBtn").textContent = "Войти";
    el("userBtn").onclick = () => (window.location.href = "index.html");
    return;
  }

  el("profileName").textContent = user.first_name || "Пользователь";
  el("avatarLetter").textContent = (user.first_name || "?").charAt(0).toUpperCase();
  el("infoEmail").textContent = user.email || "—";
  el("infoPhone").textContent = user.phone || "—";
  el("infoCar").textContent = user.number_of_car || "—";

  el("userBtn").textContent = user.first_name;
  el("userBtn").onclick = () => (window.location.href = "index.html");

  el("logoutItem").addEventListener("click", () => {
    Session.clear();
    window.location.href = "index.html";
  });
});
