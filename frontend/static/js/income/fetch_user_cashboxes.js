import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = 'http://localhost:7020/api';

export async function fetchUserCashboxes() {
  const token = await getAccessToken();
  if (!token) return [];

  const res = await fetch(`${API_URL}/auth/me/cashboxes`, {
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