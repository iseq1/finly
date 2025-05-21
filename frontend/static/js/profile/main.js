import { authGuard } from '/static/js/security/guard.js';
import { fetchUserData } from '/static/js/profile/user_info.js';
import { logout } from '/static/js/security/token.js';

(async () => {
  await authGuard();

  const user = await fetchUserData();
  if (user) {
    document.getElementById("username").textContent = user.username;
    document.getElementById("first_name").textContent = user.first_name;
    document.getElementById("last_name").textContent = user.last_name;
    document.getElementById("patronymic").textContent = user.patronymic;
    document.getElementById("phone_number").textContent = user.phone_number;
    document.getElementById("birthday").textContent = user.birthday;
    document.getElementById("email").textContent = user.email;
    document.getElementById("telegram_id").textContent = user.telegram_id;
    document.getElementById("telegram_username").textContent = user.telegram_username;
    // или любые другие данные
  }
})();

document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        logout();
      });
    }
  });