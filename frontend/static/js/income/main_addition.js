import { populateCashboxDropdown } from '/static/js/income/render_user_cashbox_combobox.js';
import { populateCategoryDropdown } from '/static/js/income/render_category_combobox.js';
import { setupCategorySubcategorySync } from '/static/js/income/render_subcategory_combobox.js';
import { handleIncomeForm } from '/static/js/income/handle_income.js';
import { authGuard } from '/static/js/security/guard.js';
import { logout } from '/static/js/security/token.js';

document.addEventListener("DOMContentLoaded", async () => {
  await authGuard();
  await populateCashboxDropdown();
  await populateCategoryDropdown();
  await setupCategorySubcategorySync();
  handleIncomeForm();
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