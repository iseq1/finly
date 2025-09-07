import { renderIncomeStatisticsTable } from '/static/js/income/render_transaction_statistic_table.js';
import { handleCategoryPopup } from '/static/js/income/handle_popup_by_category.js';
import { handleProviderPopup } from '/static/js/income/handle_popup_by_cashbox.js';
import { handleDetailPopup } from '/static/js/income/handle_popup_detail.js';
import { getDateRangeFromInputs } from '/static/js/income/utils.js';
import { hidePopup } from '/static/js/income/show_provider_popup.js';

document.addEventListener('DOMContentLoaded', async () => {

  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = new Date();
  const start_date = start.toLocaleDateString('en-CA').split('T')[0];
  const end_date = end.toLocaleDateString('en-CA').split('T')[0];

  console.log('Calling renderIncomeStatisticsTable...');
  await renderIncomeStatisticsTable({ start_date, end_date });

  // Кнопка фильтра
  const filterButton = document.querySelector('.actions input[type="submit"]');
  if (filterButton) {
    filterButton.addEventListener('click', async (event) => {
      event.preventDefault();

      const { start_date, end_date, include_empty_categories } = getDateRangeFromInputs();
      if (!start_date || !end_date) return;

      console.log('Filter clicked:', { start_date, end_date, include_empty_categories });

      await renderIncomeStatisticsTable({
        start_date,
        end_date,
        include_empty_categories
      });
    });
  }
});


document.querySelector('.popup-close')?.addEventListener('click', hidePopup);

document.addEventListener('click', async (event) => {
  const providerTh = event.target.closest('th[data-provider-id]');
  const categoryTh = event.target.closest('th[data-category-id]');
  const cell = event.target.closest('td[data-key]');

  if (providerTh) {
      handleProviderPopup(providerTh.dataset.providerId);
      return;
  }
  if (categoryTh) {
    handleCategoryPopup(categoryTh.dataset.categoryId);
    return;
  }
  if (cell) {
    const key = cell.dataset.key;
    const [providerId, categoryId] = key.split('__');
    handleDetailPopup(categoryId, providerId)
    return;
  }
});







