import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = 'http://localhost:7020/api';

export async function deleteUserCashbox(userCashboxId) {
  const token = await getAccessToken();
  if (!token) return false;

  const res = await fetch(`${API_URL}/auth/me/cashboxes/${userCashboxId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (res.status === 401) {
    logout();
    return false;
  }

  return res.ok;
}
