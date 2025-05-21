import { authGuard } from '/static/js/security/guard.js';
import { fetchUserCashboxData } from '/static/js/cashbox/user_cashboxes.js';
import { loadTable } from '/static/js/cashbox/cashbox_table_render.js';
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

  const cashboxes = await fetchUserCashboxData();
  if (!cashboxes) return;

  const container = document.getElementById("cashbox-list");
  if (!container) return;

  container.innerHTML = "";

  for (const box of cashboxes) {
    const article = document.createElement("article");
    article.classList.add("box", "transparent-after");
    article.style.position = "static";

    article.innerHTML = `
      <a href="#" class="image">
        <img src="${box.cashbox.icon}" alt="" />
      </a>
      <h3>${box.cashbox.name}</h3>
      <p>${box.custom_name || "Без кастомного наименования"}</p>
      <ul class="actions">
        <li><a href="/cashbox/${box.id}" class="button">Подробнее</a></li>
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

document.addEventListener("DOMContentLoaded", async() => {
    let userCashboxIds = new Set();
    const userCashboxes = await fetchUserCashboxData();
    userCashboxIds = new Set(userCashboxes.map(box => box.cashbox ? box.cashbox_id : null));
    let currentSortBy = null;
    let currentSortDir = 'asc';

    loadTable(1, currentSortBy, currentSortDir, userCashboxIds);

    const headers = document.querySelectorAll("table thead th[data-sort]");

    headers.forEach(header => {
    header.style.cursor = 'pointer'; // чтобы было понятно, что можно кликать
    header.addEventListener("click", () => {
        const sortField = header.getAttribute("data-sort");

        if (currentSortBy === sortField) {
        // Если уже сортируем по этому полю, меняем направление
        currentSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
        } else {
        // Если новый столбец, то по нему сортируем по возрастанию
        currentSortBy = sortField;
        currentSortDir = 'asc';
        }

        // Перезагружаем таблицу с новой сортировкой и сбрасываем страницу на 1
        loadTable(1, currentSortBy, currentSortDir, userCashboxIds);
    });
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  }
});
