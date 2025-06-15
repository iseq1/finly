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
    const article1 = document.createElement("article");
    const article2 = document.createElement("article");
    const article3 = document.createElement("article");
    article1.classList.add( "col-3", "col-12-small");
    article1.style.position = "static";
    article2.classList.add("box", "transparent-after", "col-6", "col-12-small");
    article2.style.position = "static";
    article3.classList.add( "col-3", "col-12-small");
    article3.style.position = "static";

    article1.innerHTML = ``;
    article3.innerHTML = ``;

    article2.innerHTML = `
        <h4 >
          За текущий период у Вас нет ни одного активного бюджета!
        </h4>
        <h4 >
          Это можно легко исправить!
        </h4>

      </div>
    `;
    container.appendChild(article1);
    container.appendChild(article2);
    container.appendChild(article3);
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
