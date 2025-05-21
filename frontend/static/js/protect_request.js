const API_URL = "http://localhost:7020/api";

function isLoggedIn() {
  return !!localStorage.getItem("access_token");
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/templates/auth.html";
}

async function refreshToken() {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) {
    logout();
    return;
  }

  const res = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${refresh}`,
    },
  });

  if (!res.ok) {
    logout();
    return;
  }

  const data = await res.json();
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
}

async function getAccessToken() {
  let accessToken = localStorage.getItem("access_token");
  const refresh = localStorage.getItem("refresh_token");

  // Если вообще нет токенов — редиректим
  if (!accessToken || !refresh) {
    logout();
    return null;
  }

  // Пробуем access token
  let res = await fetch(`${API_URL}/auth/ping`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  // Если токен живой — возвращаем его
  if (res.ok) {
    return accessToken;
  }

  // Если access токен протух — пробуем обновить
  if (res.status === 401) {
    try {
      const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${refresh}`,
        },
      });

      if (!refreshRes.ok) throw new Error("Refresh token invalid");

      const data = await refreshRes.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      return data.access_token;
    } catch (e) {
      // Ошибка при обновлении — логаут
      logout();
      return null;
    }
  }

  // Другие ошибки
  logout();
  return null;
}

async function authGuard() {
  const accessToken = localStorage.getItem("access_token");
  const refreshToken = localStorage.getItem("refresh_token");

  // Если токенов нет — сразу на страницу логина
  if (!accessToken || !refreshToken) {
    logout();
    return;
  }

  // Пробуем проверить токен
  const res = await fetch(`${API_URL}/auth/ping`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (res.status === 200) {
    // Всё ок, остаёмся
    return;
  }

  if (res.status === 401) {
    // Пробуем обновить
    try {
      await refreshToken();
      return;
    } catch (err) {
      // Ошибка при обновлении — выкидываем на логин
      logout();
    }
  } else {
    // Неожиданная ошибка — тоже выкидываем
    logout();
  }
}

