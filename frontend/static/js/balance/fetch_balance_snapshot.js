import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = 'http://localhost:7020/api';

export async function fetchBalanceSnapshot() {
  const token = await getAccessToken();
  if (!token) return null;

  const url = new URL(`${API_URL}/budget/balance_snapshot`);
  
  const res = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    if (res.status === 401) logout();
    return null;
  }

  return await res.json(); // массив доходов
}
