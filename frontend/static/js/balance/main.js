import { renderBalanceTable } from '/static/js/balance/render_balance_table.js';
import { fetchBalanceSnapshot } from '/static/js/balance/fetch_balance_snapshot.js';
import { authGuard } from '/static/js/security/guard.js';
import { logout } from '/static/js/security/token.js';

document.addEventListener("DOMContentLoaded", async () => {
  // Кнопка выхода
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  }

  try {
    // Защищаем страницу — если нет токена, редирект на логин
    await authGuard();

    // Получаем снапшоты баланса
    const snapshotData = await fetchBalanceSnapshot();

    // Рендерим таблицу
    renderBalanceTable(snapshotData.balance_snapshot);
  } catch (err) {
    console.error("Ошибка при инициализации страницы:", err);
    alert("Произошла ошибка при загрузке данных");
  }
});
