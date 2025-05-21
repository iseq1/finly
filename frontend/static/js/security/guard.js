import { getAccessToken, logout } from '/static/js/security/token.js';

export async function authGuard() {
  const token = await getAccessToken();
  if (!token) logout(); // внутри logout будет redirect
}
