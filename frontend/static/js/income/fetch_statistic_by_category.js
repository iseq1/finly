import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = 'http://localhost:7020/api';

export async function fetchIncomeStatisticByCategory(category_id, params) {
  const token = await getAccessToken();
  if (!token) return [];

  const res = await fetch(`${API_URL}/transactions/statistics/category/${category_id}?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    if (res.status === 401) logout();
    return [];
  }

  return await res.json();
}