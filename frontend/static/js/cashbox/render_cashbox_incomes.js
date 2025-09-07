export function renderIncomes(incomes) {
    const tbody = document.querySelector("#income-table tbody");
    tbody.innerHTML = "";
    incomes.items.forEach(income => {
      const dateObject = new Date(income.transacted_at);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${income.category.name}</td>
        <td>${income.subcategory.name}</td>
        <td>${income.amount} ${income.user_cashbox.cashbox.currency}</td>
        <td>${String(dateObject.getDate()).padStart(2, '0')}.${String(dateObject.getMonth() + 1).padStart(2, '0')}.${dateObject.getFullYear()}</td>
      `;
      tbody.appendChild(tr);
    });
  }
  