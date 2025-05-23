import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = "http://localhost:7020/api";

export async function fetchUserBudgetsData() {
  const token = await getAccessToken();
  if (!token) return null;

  const res = await fetch(`${API_URL}/budget`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    logout();
    return null;
  }

  return await res.json();
}
