import { getAccessToken, logout } from '/static/js/security/token.js';

const API_URL = 'http://localhost:7020/api';

/**
 * Обновление существующего user_cashbox
 */
export async function updateUserCashbox(userCashboxId, data) {
  const token = await getAccessToken();
  if (!token) return null;

  const res = await fetch(`${API_URL}/auth/me/cashboxes/${userCashboxId}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (res.status === 401) {
    logout();
    return null;
  }

  if (!res.ok) {
    throw new Error('Не удалось обновить кэшбокс');
  }

  return await res.json();
}

/**
 * Создание нового user_cashbox
 */
export async function createUserCashbox(data) {
  const token = await getAccessToken();
  if (!token) return null;

  const res = await fetch(`${API_URL}/auth/me/cashboxes`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (res.status === 401) {
    logout();
    return null;
  }

  if (!res.ok) {
    console.error('Ошибка сервера:', error)
    throw new Error('Не удалось создать кэшбокс');
  }

  return await res.json();
}
