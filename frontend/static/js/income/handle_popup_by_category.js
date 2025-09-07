import { fetchIncomeStatisticByCategory } from '/static/js/income/fetch_statistic_by_category.js';
import { showCategoryPopup } from '/static/js/income/show_category_popup.js';
import { getDefaultOrUrlParams } from '/static/js/income/utils.js';

export async function handleCategoryPopup(categoryId) {
  const params = getDefaultOrUrlParams();
  try {
    const data = await fetchIncomeStatisticByCategory(categoryId, params);
    if (data?.category_name) {
      showCategoryPopup(data);
    }
  } catch (err) {
    console.error('Ошибка при получении детализации категории:', err);
  }
  return;
}

