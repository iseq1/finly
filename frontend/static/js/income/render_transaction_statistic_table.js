import { fetchIncomeStatistic } from '/static/js/income/fetch_statistic.js';

export async function renderIncomeStatisticsTable({ start_date, end_date, include_empty_categories = 'true' }) {
  const tbody = document.querySelector('.table-wrapper table tbody');
  const thead = document.querySelector('.table-wrapper table thead tr');
  if (!tbody || !thead) return;

  // Собираем параметры
  const params = new URLSearchParams({
    start_date,
    end_date,
    type: 'income',
    include_empty_categories
  });

  const response = await fetchIncomeStatistic(params);
  if (!response || !response.statistics) return;

  const { statistics, category_totals, provider_totals } = response;

  // Получаем список всех провайдеров (ключи data у каждой категории одинаковы)
  const providers = Object.keys(provider_totals);

  // 🔁 Заголовки
  thead.innerHTML = `
    <th>Категория</th>
    ${providers.map(p => `<th>${p}</th>`).join('')}
    <th><strong>Итого</strong></th>
  `;

  // 🧱 Содержание
  tbody.innerHTML = '';

  for (const [categoryName, categoryInfo] of Object.entries(statistics)) {
    const row = document.createElement('tr');
    const providerData = categoryInfo.data;

    row.innerHTML = `
      <th>${categoryName}</th>
      ${providers.map(p => `<td>${providerData[p]?.sum ?? 0}</td>`).join('')}
      <td><strong>${category_totals[categoryName]}</strong></td>
    `;

    tbody.appendChild(row);
  }

  // ➕ Финальная строка — итоги по провайдерам
  const totalRow = document.createElement('tr');
  totalRow.innerHTML = `
    <th><strong>Итого</strong></th>
    ${providers.map(p => `<td><strong>${provider_totals[p]}</strong></td>`).join('')}
    <td></td>
  `;
  tbody.appendChild(totalRow);
}

export function getDateRangeFromInputs() {
  const monthStart = document.getElementById('month-start')?.value;
  const yearStart = document.getElementById('year-start')?.value;
  const monthFinish = document.getElementById('month-finish')?.value;
  const yearFinish = document.getElementById('year-finish')?.value;
  const includeEmptyCheckbox = document.getElementById('demo-human');

  let start_date, end_date;

  if (monthStart && yearStart) {
    start_date = new Date(Number(yearStart), Number(monthStart) - 1, 1);
  }
  else {
    const now = new Date();
    start_date = new Date(now.getFullYear(), now.getMonth(), 1);
  }

  if (monthFinish && yearFinish) {
    // Последний день месяца
    end_date = new Date(Number(yearFinish), Number(monthFinish), 0);
  }
  else{
    end_date = new Date();
  }

  const include_empty_categories = includeEmptyCheckbox && !includeEmptyCheckbox.checked ? 'false' : 'true';

  return {
    start_date: start_date.toISOString().split('T')[0],
    end_date: end_date.toISOString().split('T')[0],
    include_empty_categories: include_empty_categories,
  };
}