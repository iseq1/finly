import { renderPaginationControls } from '/static/js/expense/render_transaction_pagination_history_table.js';
import { fetchExpenseTransactions } from '/static/js/expense/fetch_transaction.js';

let currentFilters = {
  start_date: null,
  end_date: null,
  page: 1,
  per_page: 10,
  sort_by: 'transacted_at',
  sort_dir: 'asc',
};

export async function renderExpenseTableWithPagination({
  start_date,
  end_date,
  page = 1,
  per_page = 10,
  sort_by = 'transacted_at',
  sort_dir = 'asc'
}) {
  const tbody = document.querySelector('.table-wrapper table tbody');
  const tableWrapper = document.querySelector('.table-wrapper');
  const noDataMessage = document.querySelector('.no-data-message');
  const container = document.querySelector('.pagination');

  while (container.firstChild) {
      container.removeChild(container.firstChild);
  }

  if (!tbody || !tableWrapper || !noDataMessage) return;

  currentFilters = { start_date, end_date, page, per_page, sort_by, sort_dir };
  const params = new URLSearchParams({
    start_date,
    end_date,
    page,
    per_page,
    sort_by,
    sort_dir,
  });

  const response = await fetchExpenseTransactions(params);
  if (!response || !response.items) return;

  const { items, total, pages, has_next, has_prev } = response;
  tbody.innerHTML = '';

  if (items.length === 0) {
    tableWrapper.style.display = 'none';
    noDataMessage.style.display = 'block';
    return;
  }
  else {
    tableWrapper.style.display = 'block';
    noDataMessage.style.display = 'none';

    items.forEach(tx => {
    const tr = document.createElement('tr');

    const date = formatDate(tx.transacted_at);
    const category = tx.category?.name ?? '';
    const subcategory = tx.subcategory?.name ?? '';
    const cashbox = tx.user_cashbox?.cashbox?.name ?? '';
    const amount = tx.amount ?? 0;
    const currency = tx.user_cashbox?.cashbox?.currency ?? '';
    const comment = tx.comment || '';
    const vendor = tx.vendor || '';
    const location = tx.location || '';

    tr.innerHTML = `
      <td>${date}</td>
      <td>${category}</td>
      <td>${subcategory}</td>
      <td>${cashbox}</td>
      <td>${amount} ${currency}</td>
      <td>${comment}</td>
      <td>${vendor}</td>
      <td>${location}</td>
      <td></td>
    `;

    tbody.appendChild(tr);
  });

    renderPaginationControls(
    { page, pages, has_next, has_prev },
    (newPage) => {
      renderExpenseTableWithPagination({ ...currentFilters, page: newPage });
    }
  );
  }
}

let currentSortBy = 'transacted_at';
let currentSortDir = 'asc';


function formatDate(isoDate) {
  if (!isoDate) return '';
  const date = new Date(isoDate);
  return date.toLocaleDateString('ru-RU'); // → 22.05.2025
}

export function setupTableSorting() {
  const headers = document.querySelectorAll('.table-wrapper thead th[data-sort]');
  headers.forEach(header => {
    header.style.cursor = 'pointer';

    header.addEventListener('click', async () => {
      const sortField = header.getAttribute('data-sort');

      if (currentSortBy === sortField) {
        // Переключаем направление
        currentSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        // Меняем поле, сбрасываем на asc
        currentSortBy = sortField;
        currentSortDir = 'asc';
      }

      // Собираем текущие даты из формы (ты уже реализовал это)
      const range = getDateRangeFromInputs();
      if (!range) return;

      await renderExpenseTableWithPagination({
        ...range,
        page: 1,
        per_page: 10,
        sort_by: currentSortBy,
        sort_dir: currentSortDir,
      });
    });
  });
}

function padZero(n) {
  return n.toString().padStart(2, '0');
}

export function getDateRangeFromInputs() {
  const monthStart = document.getElementById('month-start')?.value;
  const yearStart = document.getElementById('year-start')?.value;
  const monthFinish = document.getElementById('month-finish')?.value;
  const yearFinish = document.getElementById('year-finish')?.value;

  let start_date, end_date;

  if (monthStart && yearStart) {
    start_date = new Date(Number(yearStart), Number(monthStart) - 1, 1);
  }

  if (monthFinish && yearFinish) {
    // Последний день месяца
    end_date = new Date(Number(yearFinish), Number(monthFinish), 0);
  }

  // Если нет хотя бы одной из дат — используем текущий месяц по умолчанию
  if (!start_date || !end_date) {
    const now = new Date();
    start_date = new Date(now.getFullYear(), now.getMonth(), 1);
    end_date = new Date(); // сегодня
  }

  return {
    start_date: start_date.toISOString().split('T')[0],
    end_date: end_date.toISOString().split('T')[0],
  };
}
