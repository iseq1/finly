import { fetchExpenseSubcategories } from '/static/js/expense/fetch_subcategory.js';

export function setupCategorySubcategorySync() {
  const categorySelect = document.getElementById("category");
  const subcategorySelect = document.getElementById("subcategory");

  if (!categorySelect || !subcategorySelect) return;

  categorySelect.addEventListener("change", async () => {
    const categoryId = categorySelect.value;

    subcategorySelect.innerHTML = '<option value="">- Подкатегория -</option>';

    if (!categoryId) return;

    const subcategories = await fetchExpenseSubcategories(categoryId);

    for (const sub of subcategories) {
      const option = document.createElement("option");
      option.value = sub.id;
      option.textContent = sub.name;
      subcategorySelect.appendChild(option);
    }
  });
}
