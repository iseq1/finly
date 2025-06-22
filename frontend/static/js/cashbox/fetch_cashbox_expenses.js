import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = 'http://localhost:7020/api';

export async function fetchCashboxExpenses(userCashboxId) {
  const token = await getAccessToken();
  if (!token) return null;

  const url = new URL(`${API_URL}/transactions/expense`);
  url.searchParams.set('cashbox', userCashboxId);
  url.searchParams.set('sort_by ', 'transacted_at');
  url.searchParams.set('sort_dir', 'desc');
  url.searchParams.set('page', 1);
  url.searchParams.set('per_page', 5);

  const res = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    if (res.status === 401) logout();
    return null;
  }

  return await res.json(); // массив расходов
}
