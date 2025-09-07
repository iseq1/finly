import { fetchExpenseStatisticByCategory } from '/static/js/expense/fetch_statistic_by_category.js';
import { showCategoryPopup } from '/static/js/expense/show_category_popup.js';
import { getDefaultOrUrlParams } from '/static/js/expense/utils.js';

export async function handleCategoryPopup(categoryId) {
  const params = getDefaultOrUrlParams();
  try {
    const data = await fetchExpenseStatisticByCategory(categoryId, params);
    if (data?.category_name) {
      showCategoryPopup(data);
    }
  } catch (err) {
    console.error('Ошибка при получении детализации категории:', err);
  }
  return;
}

