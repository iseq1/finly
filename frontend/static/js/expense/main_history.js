import { renderExpenseTableWithPagination, setupTableSorting, getDateRangeFromInputs } from '/static/js/expense/render_transaction_history_table.js';
import { authGuard } from '/static/js/security/guard.js';
import { logout } from '/static/js/security/token.js';


document.addEventListener("DOMContentLoaded", async () => {
  await authGuard();

  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1); // 1-е число месяца
  const end = new Date(); // сегодня
  const start_date = start.toLocaleDateString('en-CA').split('T')[0]; // YYYY-MM-DD
  const end_date = end.toLocaleDateString('en-CA').split('T')[0];     // YYYY-MM-DD
  await renderExpenseTableWithPagination({
    start_date,
    end_date,
    page: 1,
  });
  setupTableSorting();
  const filterBtn = document.querySelector('input[type="submit"].primary');
  if (filterBtn) {
    filterBtn.addEventListener('click', async (e) => {
      e.preventDefault();

      const range = getDateRangeFromInputs();
      if (!range) return;

      await renderExpenseTableWithPagination({
        ...range,
        page: 1,
        per_page: 10,
        sort_by: 'transacted_at',
        sort_dir: 'asc',
      });
    });
  }
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