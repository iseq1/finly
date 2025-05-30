import { fetchIncomeStatisticByProvider } from '/static/js/income/fetch_statistic_by_provider.js';
import { showProviderPopup } from '/static/js/income/show_provider_popup.js';
import { getDefaultOrUrlParams } from '/static/js/income/utils.js';

export async function handleProviderPopup(providerId) {
  const params = getDefaultOrUrlParams();
  try {
    const data = await fetchIncomeStatisticByProvider(providerId, params);
    if (data?.provider_name) {
      showProviderPopup(data);
    }
  } catch (err) {
    console.error('Ошибка при получении детализации провайдера:', err);
  }
  return;
}

