import { fetchIncomeCategories } from '/static/js/income/fetch_category.js';

export async function populateCategoryDropdown() {
  const selectEl = document.getElementById("category");
  if (!selectEl) return;

  const categories = await fetchIncomeCategories();

  selectEl.innerHTML = '<option value="">- Категория -</option>';

  for (const cat of categories) {
    const option = document.createElement("option");
    option.value = cat.id;
    option.textContent = `${cat.name} `;
    selectEl.appendChild(option);
  }
}
