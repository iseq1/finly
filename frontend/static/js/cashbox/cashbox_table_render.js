import { fetchCashboxData } from '/static/js/cashbox/all_cashboxes.js';
import { renderPagination } from '/static/js/cashbox/cashbox_table_pagination.js';

const tbody = document.querySelector("table tbody");
const pagination = document.querySelector(".pagination");

let currentPage = 1;
let currentSortBy = 'name';
let currentSortDir = 'asc';
const perPage = 10;

export function getCurrentPage() {
    return currentPage;
  }

export async function loadTable(page = 1, sortBy = null, sortDir = 'asc', userCashboxIds = new Set()) {
  const data = await fetchCashboxData(page, perPage, sortBy, sortDir);
  if (!data) return;
  
  const { items, pages, has_next, has_prev } = data;
  currentPage = page;
  currentSortBy = sortBy;
  currentSortDir = sortDir;

  // Очистка таблицы
  tbody.innerHTML = "";
  console.log(userCashboxIds);


  // Заполнение таблицы
  for (const item of items) {
    const owned = userCashboxIds.has(item.id);
    const liBtn = owned
      ? `<li><a href="#" class="button small">Уже есть</a></li>`
      : `<li><a href="#" class="button primary small create-btn" data-id="${item.id}">Создать</a></li>`;

    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${item.name}</td>
      <td>${item.type.name || "—"}</td>
      <td>${item.currency || "—"}</td>
      <td>${item.provider.name || "—"}</td>
      <td>
        <ul class="actions" style="margin: 0 0 0 0;">
          ${liBtn}
        </ul>
      </td>
    `;

    tbody.appendChild(tr);
  }

  document.querySelectorAll('.create-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();

      sessionStorage.removeItem('editingCashbox');

      const id = btn.dataset.id;
      const item = items.find(i => i.id === parseInt(id));
  
      if (item) {
        sessionStorage.setItem('creatingCashbox', JSON.stringify(item));
        window.location.href = `/templates/cashbox/cashbox-form.html?cashbox_id=${id}`;
      } else {
        console.error('Не найден элемент с ID:', id);
      }
    });
  });
  

  renderPagination(pages, has_prev, has_next, loadTable, currentPage, currentSortBy, currentSortDir, userCashboxIds);
}

