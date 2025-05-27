import { getAccessToken, logout } from '/static/js/security/token.js';
const API_URL = 'http://localhost:7020/api';

export async function createIncome(data) {
  const token = await getAccessToken();
  if (!token) return null;

  const res = await fetch(`${API_URL}/transactions/income`, {
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
      const errorText = await res.text(); // получаем текст ответа сервера
      console.error('Ошибка сервера:', res.status, errorText);
      throw new Error('Не удалось сохранить запись о доходе');
    }


  return await res.json();
}
