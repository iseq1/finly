import { fetchIncomeStatistic } from '/static/js/income/fetch_statistic.js';

export async function renderIncomeStatisticsTable({ start_date, end_date, include_empty_categories = 'true' }) {
  const tbody = document.querySelector('.table-wrapper table tbody');
  const thead = document.querySelector('.table-wrapper table thead tr');
  const noDataMessage = document.querySelector('.no-data-message');

  if (!tbody || !thead) return;

  const params = new URLSearchParams({
    start_date,
    end_date,
    type: 'income',
    include_empty_categories
  });

  const response = await fetchIncomeStatistic(params);

  if (!response || !response.statistics) return;

  const { statistics, category_totals, provider_totals } = response;

  // Собираем список провайдеров и их ID из первой категории
    const providerMap = new Map();

        for (const category of Object.values(statistics)) {
          for (const [providerName, info] of Object.entries(category.data)) {
            if (!providerMap.has(providerName)) {
              providerMap.set(providerName, { name: providerName, id: info.id });
            }
          }
        }

        const providers = Array.from(providerMap.values());
  // Заголовки с data-provider-id
  thead.innerHTML = `
    <th></th>
    ${providers.map(({ name, id }) => `<th data-provider-id="${id}">${name}</th>`).join('')}
    <th><strong>Итого</strong></th>
  `;

  // Содержание таблицы
  tbody.innerHTML = '';

  for (const [categoryName, categoryInfo] of Object.entries(statistics)) {
    const row = document.createElement('tr');
    const categoryId = categoryInfo.id;
    const providerData = categoryInfo.data;

    const cells = providers.map(({ name, id: providerId }) => {
      const sum = providerData[name]?.sum ?? 0;
      const dataKey = `${providerId}__${categoryId}`;
      return `<td data-key="${dataKey}">${sum}</td>`;
    }).join('');

    row.innerHTML = `
      <th data-category-id="${categoryId}">${categoryName}</th>
      ${cells}
      <td><strong>${category_totals[categoryName]}</strong></td>
    `;

    tbody.appendChild(row);
  }

  // Итоговая строка
  const totalRow = document.createElement('tr');
  totalRow.innerHTML = `
    <th><strong>Итого</strong></th>
    ${providers.map(({ id }) => `<td data-provider-id="${id}"><strong>${provider_totals[providers.find(p => p.id === id).name]}</strong></td>`).join('')}
    <td></td>
  `;
  tbody.appendChild(totalRow);
}



