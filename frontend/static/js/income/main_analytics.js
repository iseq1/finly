import { renderIncomeStatisticsTable, getDateRangeFromInputs } from '/static/js/income/render_transaction_statistic_table.js';

document.addEventListener('DOMContentLoaded', async () => {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = new Date();

  const start_date = start.toLocaleDateString('en-CA').split('T')[0];
  const end_date = end.toLocaleDateString('en-CA').split('T')[0];

  await renderIncomeStatisticsTable({ start_date, end_date });
});

document.addEventListener('DOMContentLoaded', () => {
  const filterButton = document.querySelector('.actions input[type="submit"]');
  if (!filterButton) return;

  filterButton.addEventListener('click', async (event) => {
    event.preventDefault();

    const {start_date, end_date, include_empty_categories} = getDateRangeFromInputs();
    if (!{start_date, end_date, include_empty_categories}) return;

    // 3. Вызываем функцию рендера
    await renderIncomeStatisticsTable({
      start_date,
      end_date,
      include_empty_categories
    });
  });
});