import { populateCashboxDropdown } from '/static/js/expense/render_user_cashbox_combobox.js';
import { populateCategoryDropdown } from '/static/js/expense/render_category_combobox.js';
import { setupCategorySubcategorySync } from '/static/js/expense/render_subcategory_combobox.js';
import { handleExpenseForm } from '/static/js/expense/handle_expense.js';
import { authGuard } from '/static/js/security/guard.js';
import { logout } from '/static/js/security/token.js';

document.addEventListener("DOMContentLoaded", async () => {
  await authGuard();
  await populateCashboxDropdown();
  await populateCategoryDropdown();
  await setupCategorySubcategorySync();
  handleExpenseForm();
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