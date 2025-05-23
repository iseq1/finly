import { authGuard } from '/static/js/security/guard.js';
import { fetchUserBudgetsData } from '/static/js/budget/user_budgets.js';
import { logout } from '/static/js/security/token.js';

(async () => {
  // Вставляем кастомный стиль для псевдоэлемента ::after
  const style = document.createElement('style');
  style.textContent = `
    .posts article.transparent-after::after {
      background: transparent !important;
    }
  `;
  document.head.appendChild(style);

  await authGuard();

  const container = document.getElementById("budget-list");
  if (!container) return;
  container.innerHTML = "";

  const cashboxes = await fetchUserBudgetsData();

  if (!cashboxes || cashboxes.length === 0) {
    const article = document.createElement("article");
    article.classList.add("box", "transparent-after");
    article.style.position = "static";

    article.innerHTML = `
      <div class="col-4 col-12-small"></div>
      <div class="col-4 col-12-small">
        <div class="box">
          <p>У вас пока нет ни одного зарегистрированного бюджета.</p>
          <p>Самое время исправить это!</p>
        </div>
      </div>
      <div class="col-4 col-12-small"></div>
    `;
    container.appendChild(article);
    return;
  }
  const formatter = new Intl.DateTimeFormat('ru-RU', { month: 'long' });

  for (const box of cashboxes) {
    const article = document.createElement("article");
    article.classList.add("box", "transparent-after");
    article.style.position = "static";
    const monthName = box.month
    ? formatter.format(new Date(box.year, box.month - 1))
    : "Без месяца";
    article.innerHTML = `
    <a href="#" class="image">
    </a>
    <h3>${box.comment || 'Без названия'}</h3>
    <p>За ${monthName[0].toUpperCase() + monthName.slice(1)} ${box.year || ""}</p>
    <ul class="actions">
      <li><a href="/templates/cashbox/user-cashbox.html?id=${box.id}" class="button">Подробнее</a></li>
    </ul>
  `;
  

    container.appendChild(article);
  }

  const remainder = cashboxes.length % 3;
  if (remainder !== 0) {
    const toAdd = 3 - remainder;
    for (let i = 0; i < toAdd; i++) {
      const empty = document.createElement("article");
      empty.classList.add("box");
      empty.style.visibility = "hidden";
      empty.style.position = "static";
      container.appendChild(empty);
    }
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
