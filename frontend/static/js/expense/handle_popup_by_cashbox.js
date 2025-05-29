import { fetchExpenseStatisticByProvider } from '/static/js/expense/fetch_statistic_by_provider.js';
import { showProviderPopup } from '/static/js/expense/show_provider_popup.js';
import { getDefaultOrUrlParams } from '/static/js/expense/utils.js';

export async function handleProviderPopup(providerId) {
  const params = getDefaultOrUrlParams();
  try {
    const data = await fetchExpenseStatisticByProvider(providerId, params);
    if (data?.provider_name) {
      showProviderPopup(data);
    }
  } catch (err) {
    console.error('Ошибка при получении детализации провайдера:', err);
  }
  return;
}

