import { fetchUserCashboxes } from '/static/js/income/fetch_user_cashboxes.js';

export async function populateCashboxDropdown() {
  const selectEl = document.getElementById("user_cashbox");
  if (!selectEl) return;

  const cashboxes = await fetchUserCashboxes();

  selectEl.innerHTML = '<option value="">- Ваш кэш-бокс -</option>';

  for (const cb of cashboxes) {
    const option = document.createElement("option");
    option.value = cb.id;
    option.textContent = `${cb.cashbox.name} (${cb.cashbox.currency})`;
    selectEl.appendChild(option);
  }
}
