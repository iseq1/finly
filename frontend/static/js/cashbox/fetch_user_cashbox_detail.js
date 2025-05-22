import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = "http://localhost:7020/api";

export async function fetchUserCashboxDetail(id) {
  const token = await getAccessToken();
  if (!token) return null;

  const res = await fetch(`${API_URL}/auth/me/cashboxes/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    if (res.status === 401) logout();
    return null;
  }

  return await res.json();
}
