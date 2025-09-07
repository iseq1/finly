import { fetchExpenseStatisticDetail } from '/static/js/expense/fetch_statistic_detail.js';
import { showDetailPopup } from '/static/js/expense/show_detail_popup.js';
import { getDefaultOrUrlParams } from '/static/js/expense/utils.js';

export async function handleDetailPopup(categoryId, providerId) {
  const params = getDefaultOrUrlParams();
  try {
    const data = await fetchExpenseStatisticDetail(categoryId, providerId, params);
    if (data?.category_name) {
      showDetailPopup(data);
    }
  } catch (err) {
    console.error('Ошибка при получении детализации статистики:', err);
  }
  return;
}

