document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const errorMsg = document.getElementById("error-msg");
  
    if (!form) return;
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault(); // не отправляем форму как обычно
  
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      const rememberMe = true;
  
      try {
        const response = await fetch("http://127.0.0.1:7020/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, remember_me: rememberMe }),
        });
  
        const data = await response.json();
  
        if (!response.ok) {
          errorMsg.textContent = data.message || "Ошибка входа";
          return;
        }
  
        // Сохраняем токены
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
  
        // Переход к дашборду или другой защищённой странице
        window.location.href = "/templates/profile.html";
  
      } catch (err) {
        errorMsg.textContent = "Ошибка соединения с сервером";
      }
    });
  });
  