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
  let token = localStorage.getItem("access_token");

  // Пробуем тестовый запрос для проверки
  const test = await fetch(`${API_URL}/auth/ping`, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (test.status === 401) {
    await refreshToken();
    token = localStorage.getItem("access_token");
  }

  return token;
}

function authGuard() {
  if (!isLoggedIn()) {
    window.location.href = "/templates/auth.html";
  }
}
