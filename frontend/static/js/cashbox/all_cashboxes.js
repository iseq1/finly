import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = "http://localhost:7020/api";

export async function fetchCashboxData(page = 1, per_page = 10, sortBy = null, sortDir = 'asc') {
    const token = await getAccessToken();
    if (!token) return null;
  
    const params = new URLSearchParams({ page, per_page });
    if (sortBy) {
      params.append('sort_by', sortBy);
      params.append('sort_dir', sortDir);
    }
  
    const res = await fetch(`${API_URL}/settings/cashboxes?${params.toString()}`, {
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
  
