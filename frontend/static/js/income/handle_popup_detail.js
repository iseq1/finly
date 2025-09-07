import { fetchIncomeStatisticDetail } from '/static/js/income/fetch_statistic_detail.js';
import { showDetailPopup } from '/static/js/income/show_detail_popup.js';
import { getDefaultOrUrlParams } from '/static/js/income/utils.js';

export async function handleDetailPopup(categoryId, providerId) {
  const params = getDefaultOrUrlParams();
  try {
    const data = await fetchIncomeStatisticDetail(categoryId, providerId, params);
    if (data?.category_name) {
      showDetailPopup(data);
    }
  } catch (err) {
    console.error('Ошибка при получении детализации статистики:', err);
  }
  return;
}

