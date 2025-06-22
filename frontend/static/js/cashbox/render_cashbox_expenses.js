export function renderExpenses(expenses) {
    const tbody = document.querySelector("#expense-table tbody");
    tbody.innerHTML = "";
  
    expenses.items.forEach(expense => {
      const dateObject = new Date(expense.transacted_at);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${expense.category.name}</td>
        <td>${expense.subcategory.name}</td>
        <td>${expense.amount} ${expense.user_cashbox.cashbox.currency}</td>
        <td>${String(dateObject.getDate()).padStart(2, '0')}.${String(dateObject.getMonth() + 1).padStart(2, '0')}.${dateObject.getFullYear()}</td>
      `;
      tbody.appendChild(tr);
    });
  }
  