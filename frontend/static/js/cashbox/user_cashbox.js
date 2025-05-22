import { authGuard } from '/static/js/security/guard.js';
import { fetchUserCashboxDetail } from '/static/js/cashbox/fetch_user_cashbox_detail.js';
import { renderCashboxDetail } from '/static/js/cashbox/render_user_cashbox_detail.js';
import { fetchCashboxIncomes } from '/static/js/cashbox/fetch_cashbox_incomes.js';
import { fetchCashboxExpenses } from '/static/js/cashbox/fetch_cashbox_expenses.js';
import { renderIncomes } from '/static/js/cashbox/render_cashbox_incomes.js';
import { renderExpenses } from '/static/js/cashbox/render_cashbox_expenses.js';
import { deleteUserCashbox } from '/static/js/cashbox/delete_user_cashbox.js';
import { logout } from '/static/js/security/token.js';

// Защита
authGuard();

document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
  
    if (!id) {
      alert("ID не найден в URL");
      return window.location.href = "/404.html";
    }
  
    const detail = await fetchUserCashboxDetail(id);
    if (!detail) return;
  
    renderCashboxDetail(detail);
  
    const incomes = await fetchCashboxIncomes(id);
    if (incomes) renderIncomes(incomes);
  
    const expenses = await fetchCashboxExpenses(id);
    if (expenses) renderExpenses(expenses);

    const deleteButton = document.querySelector('.button-delete');
    deleteButton.addEventListener('click', async (e) => {
    e.preventDefault();

    const confirmed = confirm("Вы уверены, что хотите удалить этот кэшбокс?");
    if (!confirmed) return;

    const success = await deleteUserCashbox(id);
    if (success) {
      alert("Кэшбокс удалён.");
      window.location.href = '/templates/cashbox/main.html'; 
    } else {
      alert("Ошибка при удалении.");
    }
  });

    document.querySelector('.button-edit').addEventListener('click', () => {
    sessionStorage.removeItem('creatingCashbox');
    sessionStorage.setItem('editingCashbox', JSON.stringify(detail));
    window.location.href = `/templates/cashbox/cashbox-form.html?id=${id}`;
  });

  
});

document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        logout();
      });
    }
  });
  