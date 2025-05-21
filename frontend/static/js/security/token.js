const API_URL = "http://localhost:7020/api";

export async function logout() {
    const refresh = localStorage.getItem("refresh_token");
  
    if (refresh) {
      try {
        await fetch(`${API_URL}/auth/logout`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${refresh}`,
          },
        });
      } catch (_) {
        // ignore errors
      }
    }
  
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/templates/auth.html";
  }
  
export async function refreshToken() {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) {
    logout();
    return null;
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
    return null;
  }

  const data = await res.json();
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  return data.access_token;
}

export async function getAccessToken() {
  let token = localStorage.getItem("access_token");

  const res = await fetch(`${API_URL}/auth/ping`, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (res.status === 200) return token;

  if (res.status === 401) return await refreshToken();

  logout();
  return null;
}
